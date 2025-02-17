import os
from pathlib import Path

import numpy as np
import torch
from torchvision.datasets.utils import download_url

import nfe.experiments.latent_ode.lib.utils as utils
from nfe.experiments.latent_ode.lib.utils import get_dict_template

DATA_DIR = Path('/opt/ml/input/data/training')
if not DATA_DIR.exists():
	DATA_DIR = Path(__file__).parents[1] / 'data/hopper'


class HopperPhysics(object):

	T = 200
	D = 14

	n_training_samples = 10000

	training_file = 'training.pt'

	def __init__(self, root, download = True, generate=False, device = torch.device('cpu')):
		self.root = root
		if download:
			self._download()

		if generate:
			self._generate_dataset()

		if not self._check_exists():
			raise RuntimeError('Dataset not found.' + ' You can use download=True to download it')

		data_file = os.path.join(self.data_folder, self.training_file)

		self.data = torch.Tensor(torch.load(data_file)).to(device)
		self.data, self.data_min, self.data_max = utils.normalize_data(self.data)

		self.device = device

	def _generate_dataset(self):
		if self._check_exists():
			return
		os.makedirs(self.data_folder, exist_ok=True)
		print('Generating dataset...')
		train_data = self._generate_random_trajectories(self.n_training_samples)
		torch.save(train_data, os.path.join(self.data_folder, self.training_file))

	def _download(self):
		if self._check_exists():
			return

		print('Downloading the dataset [325MB] ...')
		os.makedirs(self.data_folder, exist_ok=True)
		url = 'http://www.cs.toronto.edu/~rtqichen/datasets/HopperPhysics/training.pt'
		download_url(url, self.data_folder, 'training.pt', None)


	def _check_exists(self):
		return os.path.exists(os.path.join(self.data_folder, self.training_file))

	@property
	def data_folder(self):
		return DATA_DIR

	def get_dataset(self):
		return self.data

	def __len__(self):
		return len(self.data)

	def size(self, ind = None):
		if ind is not None:
			return self.data.shape[ind]
		return self.data.shape

	def __repr__(self):
		fmt_str = 'Dataset ' + self.__class__.__name__ + '\n'
		fmt_str += '    Number of datapoints: {}\n'.format(self.__len__())
		fmt_str += '    Root Location: {}\n'.format(self.root)
		return fmt_str


if __name__ == '__main__':
	hopper = HopperPhysics(root='data', download=True)
