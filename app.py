#!/usr/bin/env python3
import os

from aws_cdk import core

from panorama.panorama_stack import PanoramaStack

panorama_app = core.App()

PanoramaStack(
    panorama_app, "panorama", env={"region": os.environ["AWS_DEFAULT_REGION"]}
)

core.Tags.of(panorama_app).add("Owner", "Panorama")

panorama_app.synth()
