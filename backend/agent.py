import re
from backend.ml.inference import predict_spacings, verify_spacings

import logging

logger = logging.getLogger("sentinel-agent")

# In-memory store for Agentic State (in prod, use Redis)
agent_memory = {}

def parse_and_execute_intent(message: str, session_id: str = "default"):
    """
    A lightweight rule-based Agentic parser that mimics an LLM tool-calling agent.
    Maintains state across sessions to understand relative commands.
    In a full production scenario, this would use LangChain + OpenAI/Gemini
    with tool-calling definitions.
    """
    message_lower = message.lower()
    
    # Check for relative commands
    if session_id in agent_memory:
        last_error = agent_memory[session_id].get("last_target_error")
        if last_error:
            if "half" in message_lower:
                target_error = last_error / 2.0
                return process_target_error(target_error, session_id)
            
            relative_match = re.search(r'(reduce|decrease|tighter|increase|looser).*by\s+([0-9]*\.?[0-9]+)', message_lower)
            if relative_match:
                direction = relative_match.group(1)
                amount = float(relative_match.group(2))
                if direction in ["reduce", "decrease", "tighter"]:
                    target_error = last_error - amount
                else:
                    target_error = last_error + amount
                    
                if target_error <= 0:
                    return {"reply": "Agent: I cannot set the target error to 0 or below. Please provide a valid positive error target.", "data": None}
                return process_target_error(target_error, session_id)

    # Absolute command matching
    match = re.search(r'([0-9]*\.?[0-9]+)\s*(deg|degree|°|error|rms)', message_lower)
    if match:
        target_error = float(match.group(1))
        return process_target_error(target_error, session_id)
            
    logger.info("Agent could not extract target error from message.")
    return {
        "reply": "Agent: I can help you design radar arrays. Please specify a target RMS error (e.g., 'Design an array with 0.15 degrees error') or use relative commands like 'reduce by 0.05'.",
        "data": None
    }

def process_target_error(target_error: float, session_id: str):
    logger.info(f"Agent executing for target error: {target_error}")
    
    # Store in memory
    if session_id not in agent_memory:
        agent_memory[session_id] = {}
    agent_memory[session_id]["last_target_error"] = target_error

    # Invoke ML Model
    try:
        results = predict_spacings(target_error)
        v_results = verify_spacings(results["spacings"], target_error)
        
        reply = f"Agent: I've calculated the optimal array spacings for a target error of {target_error}°.\n\n"
        reply += f"Spacings: d1={results['spacings'][0]:.4f}m, d2={results['spacings'][1]:.4f}m, d3={results['spacings'][2]:.4f}m.\n"
        
        if v_results["acceptable"]:
            reply += f"✅ Verification Passed: The simulated achieved error is {v_results['achieved_error']:.4f}°."
        else:
            reply += f"⚠️ Warning: Achieved error {v_results['achieved_error']:.4f}° exceeds target."

        logger.info("Agent successfully parsed and executed intent.")
        return {
            "reply": reply,
            "data": results
        }
    except Exception as e:
        logger.error(f"Agent encountered an error: {e}", exc_info=True)
        return {"reply": f"Agent: I encountered an error running the ML model: {str(e)}", "data": None}
