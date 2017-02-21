from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
from sys import stdout
from collections import OrderedDict

import numpy as np
# import matplotlib.pyplot as plt

from source.posterior.core.likelihood import create_lnlikelihood
from source.tools.function_w_doc import DocFunction
from source.posterior.core.parameter import Parameter


level_logger = DEBUG
level_handler = INFO

logger = getLogger()
if logger.level != level_logger:
    logger.setLevel(level_logger)
if len(logger.handlers) == 0:
    ch = StreamHandler(stdout)
    ch.setLevel(level_handler)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
else:
    ch = logger.handlers[0]
    if ch.level != level_handler:
        ch.setLevel(level_handler)


class TestMethods(TestCase):

    def setUp(self):
        def f(p, x):
            return np.multiply(p[0], x) + p[1]

        n = 10
        self.x = range(n)
        self.a = 2
        self.b = 0.5
        self.sigma = 1.0
        self.data = f([self.a, self.b], self.x) + np.random.normal(loc=0., scale=self.sigma, size=n)
        self.data_nonoise = f([self.a, self.b], self.x)
        self.data_err = self.sigma + np.random.normal(loc=0., scale=0.01, size=n)
        arg_list = OrderedDict()
        arg_list["param"] = ["a", "b"]
        arg_list["kwargs"] = ["x"]
        self.datasimulator = DocFunction(function=f, arg_list=arg_list)
        self.jitter_multi = Parameter("jitter multi", unit="n/a",
                                      free=True, main=True,
                                      joint_prior=False, prior_category=None, prior_args=None,
                                      value=0.)

    def test_create_lnlikelihood(self):
        # datasim_func = self.datasimulator.function
        logger.info("\n\nStart test_create_lnlikelihood")
        logger.info("Test create_lnlikelihood with category='wo jitter'")
        lnlike = create_lnlikelihood(self.datasimulator, self.data_nonoise, self.data_err,
                                     category="wo jitter", jitter_param=None)
        logger.info("Arg_list of the lnlike function:\n{}".format(lnlike.arg_list))
        res_good = lnlike.function([self.a, self.b], self.data_nonoise, self.data_err, x=self.x)
        logger.info("lnlike value with good parameters:\n{}".format(res_good))
        res_off = lnlike.function([self.a - 0.01, self.b - 0.01], self.data_nonoise, self.data_err,
                                  x=self.x)
        logger.info("lnlike value with slightly off parameters:\n{}".format(res_off))

        logger.info("Test create_lnlikelihood with category='jitter multiplicative'")
        lnlike = create_lnlikelihood(self.datasimulator, self.data, self.data_err,
                                     category="jitter multiplicative",
                                     jitter_param=self.jitter_multi)
        logger.info("Arg_list of the lnlike function:\n{}".format(lnlike.arg_list))
        res_good = lnlike.function([0., self.a, self.b], self.data, self.data_err, x=self.x)
        logger.info("lnlike value with good parameters and good jitter:\n{}".format(res_good))
        res_slightover = lnlike.function([1., self.a, self.b], self.data, self.data_err, x=self.x)
        logger.info("lnlike value with good parameters and slightly overestimated jitter:\n{}"
                    "".format(res_slightover))
        res_over = lnlike.function([10., self.a, self.b], self.data, self.data_err, x=self.x)
        logger.info("lnlike value with good parameters and really overestimated jitter:\n{}"
                    "".format(res_over))
        res_under = lnlike.function([-1., self.a, self.b], self.data, self.data_err, x=self.x)
        logger.info("lnlike value with good parameters and slightly underestimated jitter:\n{}"
                    "".format(res_under))
        # plt.errorbar(self.x, self.data, yerr=self.data_err, color="b")
        # plt.plot(self.x, self.data_nonoise, "g+")
        # plt.plot(self.x, self.datasimulator.function([self.a-0.1, self.b],self.x), "r+")
        # plt.show()


if __name__ == '__main__':
    main()
