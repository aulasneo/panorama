#!/usr/bin/env python3
import os

from aws_cdk import core

from panorama.panorama_stack import PanoramaStack

app = core.App()
PanoramaStack(app, "panorama", env={"region": os.environ["AWS_DEFAULT_REGION"]})

app.synth()
