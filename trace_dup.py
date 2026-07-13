import gdsfactory as gf
from amf.chp import PDK; PDK.activate()
from loguru import logger
import sys, traceback

def sink(message):
    if "duplicat" in message.record["message"].lower():
        traceback.print_stack()
        print(">>> DUP LOGGED ABOVE <<<", file=sys.stderr)

logger.remove()
logger.add(sink, level="ERROR")

gf.clear_cache()
from myamf.Main_v2 import Main_v2
Main_v2()
print("build done")
