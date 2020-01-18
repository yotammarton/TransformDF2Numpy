import numpy as np
from .errors import *


def one_hot_encode(transformer, numpy_array):
    if not transformer.categoricals():
        raise NoCategoricalVariableError

    if len(numpy_array.shape) != 2:
        raise InvalidNumpyArrayShapeError

    if numpy_array.shape[1] != len(transformer.variables()):
        raise InvalidNumpyArrayColumnsError

    # initialize output numpy array
    num_vars = sum(transformer.nuniques()) + transformer.num_numericals
    out = np.zeros([numpy_array.shape[0], num_vars])

    start_index = 0
    names = []
    for category_index, var_name in enumerate(transformer.categoricals()):
        end_index = start_index + transformer.nunique(category_index)
        # one hot encoding
        out[:, start_index:end_index] \
            = np.identity(transformer.nunique(category_index))[list(numpy_array[:, category_index].astype(np.int))]

        # nan (factorized value: -1) handling
        if (numpy_array[:, category_index] == -1).sum():
            drop_target_indices = list(np.where(numpy_array[:, category_index] == -1)[0])
            out[drop_target_indices, start_index:end_index] = 0.

        # scale one hot variables if the transformer's scaling flag is True
        if transformer.numerical_scaling:
            fac = transformer._get_transform(category_index)
            out[:, start_index:end_index] = (out[:, start_index:end_index] - fac.categories_one_hot_means) \
                                            / fac.categories_one_hot_stds

        # create variable names like ["variable1_category1", "variable1_category2", ... ]
        heads = np.array([var_name + "_"] * len(transformer.categories(category_index)))
        names += list(np.core.defchararray.add(heads, list(transformer.categories(category_index))))

        start_index = end_index

    out[:, end_index:] = numpy_array[:, transformer.num_categoricals:]
    out_names = names + transformer.numericals()

    return out, out_names

