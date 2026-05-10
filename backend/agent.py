import re
import logging
from typing import Callable, Dict, Any

from backend.ml.inference import predict_spacings, verify_spacings
from backend.db.database import SessionLocal
from backend.db.models import ChatSession

logger = logging.getLogger("sentinel-agent")

class Tool:
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func

class AgentExecutor:
    """
    ReAct (Reasoning + Acting) Agent Executor Architecture.
    Maintains a tool registry and state across sessions.
    """
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_tools()

    def _register_tools(self):
        self.tools["predict_and_verify"] = Tool(
            name="predict_and_verify",
            description="Predicts optimal array spacings for a given target RMS error and verifies the result.",
            func=self._tool_predict_and_verify
        )
        self.tools["adjust_relative"] = Tool(
            name="adjust_relative",
            description="Adjusts the previously configured target error by a relative amount.",
            func=self._tool_adjust_relative
        )
        self.tools["help"] = Tool(
            name="help",
            description="Provides instructions on how to use the agent.",
            func=self._tool_help
        )

    def _tool_predict_and_verify(self, target_error: float, session_id: str) -> Dict[str, Any]:
        logger.info(f"Tool 'predict_and_verify' executing for target error: {target_error}")
        
        # Persist to DB
        db = SessionLocal()
        try:
            session_obj = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
            if not session_obj:
                session_obj = ChatSession(session_id=session_id, last_target_error=target_error)
                db.add(session_obj)
            else:
                session_obj.last_target_error = target_error
            db.commit()
        finally:
            db.close()

        try:
            results = predict_spacings(target_error)
            v_results = verify_spacings(results["spacings"], target_error)
            
            reply = f"Agent: I've calculated the optimal array spacings for a target error of {target_error}°.\n\n"
            reply += f"Spacings: d1={results['spacings'][0]:.4f}m, d2={results['spacings'][1]:.4f}m, d3={results['spacings'][2]:.4f}m.\n"
            
            if v_results["acceptable"]:
                reply += f"✅ Verification Passed: The simulated achieved error is {v_results['achieved_error']:.4f}°."
            else:
                reply += f"⚠️ Warning: Achieved error {v_results['achieved_error']:.4f}° exceeds target."

            return {"reply": reply, "data": results}
        except Exception as e:
            logger.error(f"Tool error: {e}", exc_info=True)
            return {"reply": f"Agent: I encountered an error running the ML model: {str(e)}", "data": None}

    def _tool_adjust_relative(self, direction: str, amount: float, session_id: str) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            session_obj = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
            if not session_obj or session_obj.last_target_error is None:
                return {"reply": "Agent: I don't have a previous configuration to adjust. Please provide an absolute target first.", "data": None}
            last_error = session_obj.last_target_error
        finally:
            db.close()
        
        if direction == "half":
            target_error = last_error / 2.0
        elif direction in ["reduce", "decrease", "tighter"]:
            target_error = last_error - amount
        else:
            target_error = last_error + amount
            
        if target_error <= 0:
            return {"reply": "Agent: I cannot set the target error to 0 or below. Please provide a valid positive error target.", "data": None}
            
        return self._tool_predict_and_verify(target_error, session_id)

    def _tool_help(self, *args, **kwargs) -> Dict[str, Any]:
        return {
            "reply": "Agent: I can help you design radar arrays. Please specify a target RMS error (e.g., 'Design an array with 0.15 degrees error') or use relative commands like 'reduce by 0.05'.",
            "data": None
        }

    def parse_and_execute(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        NLU Router: Parses intent and dispatches to the correct tool.
        """
        message_lower = message.lower()
        
        # 1. Intent: Adjust Relative (Half)
        if "half" in message_lower:
            return self.tools["adjust_relative"].func("half", 0.0, session_id)
            
        # 2. Intent: Adjust Relative (Math)
        relative_match = re.search(r'(reduce|decrease|tighter|increase|looser).*by\s+([0-9]*\.?[0-9]+)', message_lower)
        if relative_match:
            direction = relative_match.group(1)
            amount = float(relative_match.group(2))
            return self.tools["adjust_relative"].func(direction, amount, session_id)

        # 3. Intent: Absolute Predict
        absolute_match = re.search(r'([0-9]*\.?[0-9]+)\s*(deg|degree|°|error|rms)', message_lower)
        if absolute_match:
            target_error = float(absolute_match.group(1))
            return self.tools["predict_and_verify"].func(target_error, session_id)
            
        # 4. Intent: Unknown / Help
        return self.tools["help"].func()

# Singleton instance
executor = AgentExecutor()

def parse_and_execute_intent(message: str, session_id: str = "default"):
    return executor.parse_and_execute(message, session_id)
