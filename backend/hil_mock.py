import time
import logging

logger = logging.getLogger("sentinel-hil")

def deploy_to_hardware(spacings: list, snr_db: float):
    """
    Mock service to simulate sending SCPI commands to a physical SDR/FPGA radar array.
    """
    logger.info("Initializing connection to mock SDR hardware via TCP/IP...")
    time.sleep(0.5) # Simulate network latency
    
    logger.info("Sending array spacing configuration: " + str(spacings))
    # Simulated SCPI commands
    commands = [
        "*RST",
        f":ROUT:ARR:SPAC:ELEM1 {spacings[0]:.6f}",
        f":ROUT:ARR:SPAC:ELEM2 {spacings[1]:.6f}",
        f":ROUT:ARR:SPAC:ELEM3 {spacings[2]:.6f}",
        f":CONF:SNR {snr_db:.1f}",
        ":INIT:IMM"
    ]
    
    for cmd in commands:
        logger.debug(f"SCPI -> {cmd}")
        time.sleep(0.1) # Simulate serial write time
        
    logger.info("Hardware deployment successful.")
    return {
        "status": "success",
        "message": "Configuration successfully deployed to mock hardware.",
        "commands_sent": len(commands)
    }
