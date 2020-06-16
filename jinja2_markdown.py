#!/usr/bin/env python3

import jinja2
import os

markdown_jinja_env = jinja2.Environment(
    trim_blocks = True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(os.path.abspath('.'))
)
