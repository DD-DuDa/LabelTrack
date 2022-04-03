#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (c) Megvii, Inc. and its affiliates.

import os

from yolox.exp import Exp as MyExp


class Exp(MyExp):
    def __init__(self):
        super(Exp, self).__init__()
        self.num_classes = 11
        self.depth = 0.67
        self.width = 0.75
        self.random_size = (18, 32)
        self.test_size = (800, 1440)
        self.test_conf = 0.25
        self.nmsthre = 0.45
        self.exp_name = os.path.split(os.path.realpath(__file__))[1].split(".")[0]

