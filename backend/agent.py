import re
from backend.ml.inference import predict_spacings, verify_spacings

import logging

logger = logging.getLogger("sentinel-agent")

def parse_and_execute_intent(message: str):
    """
    A lightweight rule-based Agentic parser that mimics an LLM tool-calling agent.
    In a full production scenario, this would use LangChain + OpenAI/Gemini
    with tool-calling definitions.
    """
    message = message.lower()
    
    # Extract target error if mentioned
    match = re.search(r'([0-9]*\.?[0-9]+)\s*(deg|degree|°|error|rms)', message)
    if match:
        target_error = float(match.group(1))
        logger.info(f"Agent extracted target error: {target_error}")
        
        # Invoke ML Model
        try:
            results = predict_spacings(target_error)
            spacings = results["spacings"]
            positions = results["positions"]
            
            # Verify
            v_results = verify_spacings(spacings, target_error)
            
            reply = (
                f"Agent: I have designed the radar array to meet your **{target_error}°** RMS error target.\n\n"
                f"**Optimal Spacings**: d1={spacings[0]:.4f}m, d2={spacings[1]:.4f}m, d3={spacings[2]:.4f}m\n"
                f"**Total Aperture**: {positions[-1]:.4f}m\n\n"
            )
            if v_results["acceptable"]:
                reply += "✅ Simulated verification passed."
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
            
    logger.info("Agent could not extract target error from message.")
    return {
        "reply": "Agent: I can help you design radar arrays. Please specify a target RMS error, like 'Design an array with 0.15 degrees error'.",
        "data": None
    }
