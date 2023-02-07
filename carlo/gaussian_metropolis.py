"""
Module containing Markov Chains Monte Carlo sampler utilizing Metropolis algorithm
with Gaussian proposal distribution.
"""

import numpy as np
from carlo import base_sampler


class GaussianMetropolis(base_sampler.BaseSampler):
    def __init__(self, target) -> None:
        """
        Initializes the problem sampler object.

        :param target: Target distribution to be sampled from. This should either be
        posterior distribution of the model or a product of prior distribution and
        likelihood.
        :type target: function
        """

        super().__init__()
        self.target = target

    def _iterate(self, theta_current, step_size, **kwargs):
        """
        Single iteration of the sampler

        :param theta_current: Vector of current values of parameter(s)
        :type theta_current: ndarray
        :param step_size: Proposal step size equal to the standard deviation of
        of the proposal distribution
        :type step_size: float
        :return: New value of parameter vector, acceptance information
        :rtype: ndarray, int
        """

        theta_proposed = np.random.normal(loc=theta_current, scale=step_size)
        alpha = min(
            1,
            np.exp(
                self.target(theta_proposed, **kwargs)
                - self.target(theta_current, **kwargs)
            ),
        )
        u = np.random.rand()
        if u <= alpha:
            theta_new = theta_proposed
            a = 1
        else:
            theta_new = theta_current
            a = 0

        return theta_new, a

    def sample(self, iter, warmup, theta, step_size, lag=1, **kwargs):
        """
        Samples from the target distribution

        :param iter: Number of iterations of the algorithm
        :type iter: int
        :param warmup: Number of warmup steps of the algorithm. These are discarded
        so that the only samples recorded are the ones obtained after the Markov chain
        has reached the stationary distribution
        :type warmup: int
        :param theta: Vector of initial values of parameter(s)
        :type theta: ndarray
        :param step_size: Proposal step size equal to the standard deviation of
        of the proposal distribution
        :type step_size: float
        :param lag: Sampler lag. Parameter specifying every how many iterations will the sample
        be recorded. Used to limit autocorrelation of the samples. If `lag=1`, every sample is
        recorded, if `lag=3` each third sample is recorded, etc. , defaults to 1
        :type lag: int, optional
        :return: Numpy array of samples for every parameter, for every algorithm iteration,
        numpy array of acceptance information for every algorithm iteration.
        :rtype: ndarray, ndarray
        """

        samples = np.zeros(iter)
        acceptances = np.zeros(iter)

        for i in range(warmup):
            theta, a = self._iterate(theta, step_size, **kwargs)

        for i in range(iter):
            for _ in range(lag):
                theta, a = self._iterate(theta, step_size, **kwargs)
            samples[i] = theta
            acceptances[i] = a

        self.samples = samples
        self.acceptances = acceptances

        return samples, acceptances
