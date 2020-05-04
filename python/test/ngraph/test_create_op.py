# ******************************************************************************
# Copyright 2017-2020 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************
import numpy as np
import pytest

import ngraph as ng

integral_np_types = [np.int8, np.int16, np.int32, np.int64,
                     np.uint8, np.uint16, np.uint32, np.uint64]


@pytest.mark.parametrize('dtype', integral_np_types)
def test_interpolate(dtype):
    image_shape = [1, 3, 1024, 1024]
    output_shape = [64, 64]
    attributes = {
        'InterpolateAttrs.axes': [2, 3],
        'InterpolateAttrs.mode': 'cubic',
        'InterpolateAttrs.pads_begin': np.array([2, 2], dtype=dtype),
    }

    image_node = ng.parameter(image_shape, dtype, name='Image')

    node = ng.interpolate(image_node, output_shape, attributes)
    expected_shape = [1, 3, 64, 64]

    assert node.get_type_name() == 'Interpolate'
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == expected_shape


@pytest.mark.parametrize('int_dtype, fp_dtype', [
    (np.int8, np.float32),
    (np.int16, np.float32),
    (np.int32, np.float32),
    (np.int64, np.float32),
    (np.uint8, np.float32),
    (np.uint16, np.float32),
    (np.uint32, np.float32),
    (np.uint64, np.float32),
    (np.int32, np.float16),
    (np.int32, np.float64),
])
def test_prior_box(int_dtype, fp_dtype):
    image_shape = np.array([64, 64], dtype=int_dtype)
    attributes = {
        'PriorBoxAttrs.offset': fp_dtype(0),
        'PriorBoxAttrs.min_size': np.array([2, 3], dtype=fp_dtype),
        'PriorBoxAttrs.aspect_ratio': np.array([1.5, 2.0, 2.5], dtype=fp_dtype),
    }

    layer_shape = ng.constant(np.array([32, 32], dtype=int_dtype), int_dtype)

    node = ng.prior_box(layer_shape, image_shape, attributes)

    assert node.get_type_name() == 'PriorBox'
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [2, 20480]


@pytest.mark.parametrize('int_dtype, fp_dtype', [
    (np.int8, np.float32),
    (np.int16, np.float32),
    (np.int32, np.float32),
    (np.int64, np.float32),
    (np.uint8, np.float32),
    (np.uint16, np.float32),
    (np.uint32, np.float32),
    (np.uint64, np.float32),
    (np.int32, np.float16),
    (np.int32, np.float64),
])
def test_prior_box_clustered(int_dtype, fp_dtype):
    image_size = np.array([64, 64], dtype=int_dtype)
    attributes = {
        'PriorBoxClusteredAttrs.offset': fp_dtype(0.5),
        'PriorBoxClusteredAttrs.widths': np.array([4.0, 2.0, 3.2], dtype=fp_dtype),
        'PriorBoxClusteredAttrs.heights': np.array([1.0, 2.0, 1.0], dtype=fp_dtype),
    }

    output_size = ng.constant(np.array([19, 19], dtype=int_dtype), int_dtype)

    node = ng.prior_box_clustered(output_size, image_size, attributes)

    assert node.get_type_name() == 'PriorBoxClustered'
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [2, 4332]


@pytest.mark.parametrize('int_dtype, fp_dtype', [
    (np.int8, np.float32),
    (np.int16, np.float32),
    (np.int32, np.float32),
    (np.int64, np.float32),
    (np.uint8, np.float32),
    (np.uint16, np.float32),
    (np.uint32, np.float32),
    (np.uint64, np.float32),
    (np.int32, np.float16),
    (np.int32, np.float64),
])
def test_detection_output(int_dtype, fp_dtype):
    attributes = {
        'DetectionOutputAttrs.num_classes': int_dtype(85),
        'DetectionOutputAttrs.keep_top_k': np.array([64], dtype=int_dtype),
        'DetectionOutputAttrs.nms_threshold': fp_dtype(0.645),
    }

    box_logits = ng.parameter([4, 1, 5, 5], fp_dtype, 'box_logits')
    class_preds = ng.parameter([2, 1, 4, 5], fp_dtype, 'class_preds')
    proposals = ng.parameter([2, 1, 4, 5], fp_dtype, 'proposals')
    aux_class_preds = ng.parameter([2, 1, 4, 5], fp_dtype, 'aux_class_preds')
    aux_box_preds = ng.parameter([2, 1, 4, 5], fp_dtype, 'aux_box_preds')

    node = ng.detection_output(box_logits, class_preds, proposals, attributes, aux_class_preds,
                               aux_box_preds)

    assert node.get_type_name() == 'DetectionOutput'
    assert node.get_output_size() == 1
    assert list(node.get_output_shape(0)) == [1, 1, 256, 7]


@pytest.mark.parametrize('int_dtype, fp_dtype', [
    (np.uint8, np.float32),
    (np.uint16, np.float32),
    (np.uint32, np.float32),
    (np.uint64, np.float32),
    (np.uint32, np.float16),
    (np.uint32, np.float64),
])
def test_proposal(int_dtype, fp_dtype):
    attributes = {
        'ProposalAttrs.base_size': int_dtype(1),
        'ProposalAttrs.pre_nms_topn': int_dtype(20),
        'ProposalAttrs.post_nms_topn': int_dtype(64),
        'ProposalAttrs.nms_thresh': fp_dtype(0.34),
        'ProposalAttrs.feat_stride': int_dtype(16),
        'ProposalAttrs.min_size': int_dtype(32),
        'ProposalAttrs.ratio': np.array([0.1, 1.5, 2.0, 2.5], dtype=fp_dtype),
        'ProposalAttrs.scale': np.array([2, 3, 3, 4], dtype=fp_dtype),
    }
    batch_size = 7

    class_probs = ng.parameter([batch_size, 12, 34, 62], fp_dtype, 'class_probs')
    class_logits = ng.parameter([batch_size, 24, 34, 62], fp_dtype, 'class_logits')
    image_shape = ng.parameter([3], fp_dtype, 'image_shape')
    node = ng.proposal(class_probs, class_logits, image_shape, attributes)

    assert node.get_type_name() == 'Proposal'
    assert node.get_output_size() == 1
    assert (list(node.get_output_shape(0))
            == [batch_size * attributes['ProposalAttrs.post_nms_topn'], 5])
