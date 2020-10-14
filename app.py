#!/usr/bin/env python3

from aws_cdk import core

from panorama.panorama_stack import PanoramaStack


app = core.App()
PanoramaStack(app, "panorama")

app.synth()
