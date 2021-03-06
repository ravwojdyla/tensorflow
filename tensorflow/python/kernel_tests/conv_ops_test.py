"""Functional tests for convolutional operations."""
import math

import tensorflow.python.platform

import numpy as np
import tensorflow as tf

from tensorflow.python.kernel_tests import gradient_checker as gc


def GetInceptionShapes():
  """Iterator for the convolution shapes used in the Inception 2015 model.

  Yields:
    Tuple (input_size, filter_size, out_size, stride, padding), the convolution
    parameters of Inception layers.
  """
  input_sizes = [[4, 5, 5, 1248], [4, 8, 8, 384], [4, 8, 8, 384],
                 [4, 8, 8, 2048], [4, 8, 8, 448], [4, 8, 8, 2048],
                 [4, 8, 8, 2048], [4, 8, 8, 2048], [4, 8, 8, 1760],
                 [4, 8, 8, 1760], [4, 8, 8, 1760], [4, 8, 8, 1760],
                 [4, 17, 17, 192], [4, 17, 17, 192], [4, 17, 17, 1248],
                 [4, 17, 17, 128], [4, 17, 17, 1248], [4, 17, 17, 224],
                 [4, 17, 17, 192], [4, 17, 17, 192], [4, 17, 17, 1216],
                 [4, 17, 17, 1216], [4, 17, 17, 224], [4, 17, 17, 192],
                 [4, 17, 17, 192], [4, 17, 17, 1152], [4, 17, 17, 1152],
                 [4, 17, 17, 192], [4, 17, 17, 160], [4, 17, 17, 1152],
                 [4, 17, 17, 1024], [4, 17, 17, 128], [4, 17, 17, 1024],
                 [4, 17, 17, 128], [4, 17, 17, 1024], [4, 17, 17, 128],
                 [4, 17, 17, 768], [4, 17, 17, 128], [4, 17, 17, 128],
                 [4, 17, 17, 768], [4, 17, 17, 768], [4, 35, 35, 96],
                 [4, 35, 35, 288], [4, 35, 35, 64], [4, 35, 35, 288],
                 [4, 35, 35, 256], [4, 35, 35, 48], [4, 35, 35, 256],
                 [4, 35, 35, 96], [4, 35, 35, 192], [4, 35, 35, 192],
                 [4, 35, 35, 192], [4, 73, 73, 64], [4, 73, 73, 64],
                 [4, 147, 147, 24]]
  filter_sizes = [[1, 1, 1248, 128], [1, 3, 384, 384], [3, 1, 384, 384],
                  [1, 1, 2048, 192], [3, 3, 448, 384], [1, 1, 2048, 320],
                  [1, 1, 2048, 448], [1, 1, 2048, 384], [1, 1, 1760, 384],
                  [1, 1, 1760, 192], [1, 1, 1760, 448], [1, 1, 1760, 320],
                  [3, 3, 192, 192], [3, 3, 192, 192], [1, 1, 1248, 192],
                  [3, 3, 128, 320], [1, 1, 1248, 128], [1, 3, 224, 224],
                  [3, 1, 192, 256], [1, 3, 192, 256], [1, 1, 1216, 192],
                  [1, 1, 1216, 96], [3, 1, 224, 224], [3, 3, 192, 224],
                  [1, 3, 192, 192], [1, 1, 1152, 192], [1, 1, 1152, 128],
                  [3, 1, 192, 192], [3, 3, 160, 192], [1, 1, 1152, 160],
                  [1, 1, 1024, 128], [1, 3, 128, 192], [1, 1, 1024, 160],
                  [3, 1, 128, 192], [1, 1, 1024, 256], [3, 1, 128, 128],
                  [1, 1, 768, 192], [1, 3, 128, 128], [3, 3, 128, 128],
                  [1, 1, 768, 128], [1, 1, 768, 320], [3, 3, 96, 96],
                  [3, 3, 288, 384], [3, 3, 64, 96], [1, 1, 288, 64],
                  [1, 1, 256, 64], [5, 5, 48, 64], [1, 1, 256, 48],
                  [3, 3, 96, 96], [1, 1, 192, 32], [1, 1, 192, 64],
                  [1, 1, 192, 48], [3, 3, 64, 192], [1, 1, 64, 64],
                  [1, 1, 24, 64]]
  out_sizes = [[4, 5, 5, 128], [4, 8, 8, 384], [4, 8, 8, 384],
               [4, 8, 8, 192], [4, 8, 8, 384], [4, 8, 8, 320],
               [4, 8, 8, 448], [4, 8, 8, 384], [4, 8, 8, 384],
               [4, 8, 8, 192], [4, 8, 8, 448], [4, 8, 8, 320],
               [4, 8, 8, 192], [4, 17, 17, 192], [4, 17, 17, 192],
               [4, 8, 8, 320], [4, 17, 17, 128], [4, 17, 17, 224],
               [4, 17, 17, 256], [4, 17, 17, 256], [4, 17, 17, 192],
               [4, 17, 17, 96], [4, 17, 17, 224], [4, 17, 17, 224],
               [4, 17, 17, 192], [4, 17, 17, 192], [4, 17, 17, 128],
               [4, 17, 17, 192], [4, 17, 17, 192], [4, 17, 17, 160],
               [4, 17, 17, 128], [4, 17, 17, 192], [4, 17, 17, 160],
               [4, 17, 17, 192], [4, 17, 17, 256], [4, 17, 17, 128],
               [4, 17, 17, 192], [4, 17, 17, 128], [4, 17, 17, 128],
               [4, 17, 17, 128], [4, 17, 17, 320], [4, 17, 17, 96],
               [4, 17, 17, 384], [4, 35, 35, 96], [4, 35, 35, 64],
               [4, 35, 35, 64], [4, 35, 35, 64], [4, 35, 35, 48],
               [4, 35, 35, 96], [4, 35, 35, 32], [4, 35, 35, 64],
               [4, 35, 35, 48], [4, 71, 71, 192], [4, 73, 73, 64],
               [4, 147, 147, 64]]
  strides = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
             1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
  # pylint: disable=invalid-name
  VALID = "VALID"
  SAME = "SAME"
  # pylint: enable=invalid-name
  paddings = [SAME, SAME, SAME, SAME, SAME, SAME, SAME, SAME,
              SAME, SAME, SAME, SAME, VALID, SAME, SAME, VALID,
              SAME, SAME, SAME, SAME, SAME, SAME, SAME, SAME,
              SAME, SAME, SAME, SAME, SAME, SAME, SAME, SAME,
              SAME, SAME, SAME, SAME, SAME, SAME, SAME, SAME,
              SAME, VALID, VALID, SAME, SAME, SAME, SAME, SAME,
              SAME, SAME, SAME, SAME, VALID, VALID, VALID]
  for i, f, o, s, p in zip(input_sizes, filter_sizes, out_sizes,
                           strides, paddings):
    yield i, f, o, s, p


class Conv2DTest(tf.test.TestCase):

  def _SetupValuesForDevice(self, tensor_in_sizes, filter_in_sizes, stride,
                            padding, use_gpu):
    """Verifies the output values of the convolution function.

    Args:
      tensor_in_sizes: Input tensor dimensions in
        [batch, input_rows, input_cols, input_depth].
      filter_in_sizes: Filter tensor dimensions in
        [kernel_rows, kernel_cols, input_depth, output_depth].
      stride: Stride.
      padding: Padding type.
      use_gpu: True if the operations should be run on GPU
    Returns:
      Symbolic tensor value that can be used to execute the computation
    """
    total_size_1 = 1
    total_size_2 = 1
    for s in tensor_in_sizes:
      total_size_1 *= s
    for s in filter_in_sizes:
      total_size_2 *= s
    # Initializes the input tensor with array containing incrementing
    # numbers from 1.
    x1 = [f * 1.0 for f in range(1, total_size_1 + 1)]
    x2 = [f * 1.0 for f in range(1, total_size_2 + 1)]
    with self.test_session(use_gpu=use_gpu) as sess:
      t1 = tf.constant(x1, shape=tensor_in_sizes)
      t2 = tf.constant(x2, shape=filter_in_sizes)
      conv = tf.nn.conv2d(t1, t2,
                           strides=[1, stride, stride, 1],
                           padding=padding)
      return conv

  def _CompareFwdValues(self, tensor_in_sizes, filter_in_sizes,
                        stride, padding):
    """Verifies that CPU and GPU produce the same values.

    Args:
      tensor_in_sizes: Input tensor dimensions in
        [batch, input_rows, input_cols, input_depth].
      filter_in_sizes: Filter tensor dimensions in
        [kernel_rows, kernel_cols, input_depth, output_depth].
      stride: Stride.
      padding: Padding type.
    """
    x1 = np.random.rand(*tensor_in_sizes).astype(np.float32)
    x2 = np.random.rand(*filter_in_sizes).astype(np.float32)
    def _SetupVal(use_gpu):
      with self.test_session(use_gpu=use_gpu):
        t1 = tf.constant(x1, shape=tensor_in_sizes)
        t2 = tf.constant(x2, shape=filter_in_sizes)
        conv = tf.nn.conv2d(t1, t2, strides=[1, stride, stride, 1],
                             padding=padding)
        return conv
    gpu_tensor = _SetupVal(use_gpu=True)
    cpu_tensor = _SetupVal(use_gpu=False)
    with self.test_session() as sess:
      (gpu_value, cpu_value) = sess.run([gpu_tensor, cpu_tensor])
      self.assertAllClose(cpu_value, gpu_value, rtol=1e-5, atol=1e-5)

  def _VerifyValues(self, tensor_in_sizes, filter_in_sizes, stride,
                    padding, expected):
    tensor_cpu = self._SetupValuesForDevice(tensor_in_sizes, filter_in_sizes,
                                            stride, padding, use_gpu=False)
    tensor_gpu = self._SetupValuesForDevice(tensor_in_sizes, filter_in_sizes,
                                            stride, padding, use_gpu=True)
    with self.test_session() as sess:
      tensors = [tensor_cpu, tensor_gpu]
      (value_cpu, value_gpu) = sess.run(tensors)
      values = [value_cpu, value_gpu]
      for i in range(len(tensors)):
        conv = tensors[i]
        value = values[i]
        print "expected = ", expected
        print "actual = ", value
        self.assertArrayNear(expected, np.ravel(value), 1e-5)
        self.assertShapeEqual(value, conv)

  def testConv2D1x1Filter(self):
    expected_output = [30.0, 36.0, 42.0, 66.0, 81.0, 96.0, 102.0, 126.0, 150.0,
                       138.0, 171.0, 204.0, 174.0, 216.0, 258.0, 210.0, 261.0,
                       312.0]
    self._VerifyValues(tensor_in_sizes=[1, 2, 3, 3],
                       filter_in_sizes=[1, 1, 3, 3],
                       stride=1, padding="VALID",
                       expected=expected_output)

  def testConv2D2x2Filter(self):
    # The outputs are computed using third_party/py/IPython/notebook.
    expected_output = [2271.0, 2367.0, 2463.0, 2901.0, 3033.0, 3165.0]
    self._VerifyValues(tensor_in_sizes=[1, 2, 3, 3],
                       filter_in_sizes=[2, 2, 3, 3],
                       stride=1, padding="VALID",
                       expected=expected_output)

  def testConv2D1x2Filter(self):
    # The outputs are computed using third_party/py/IPython/notebook.
    expected_output = [231.0, 252.0, 273.0, 384.0, 423.0, 462.0, 690.0,
                       765.0, 840.0, 843.0, 936.0, 1029.0]
    self._VerifyValues(tensor_in_sizes=[1, 2, 3, 3],
                       filter_in_sizes=[1, 2, 3, 3],
                       stride=1, padding="VALID",
                       expected=expected_output)

  def testConv2D2x2FilterStride2(self):
    expected_output = [2271.0, 2367.0, 2463.0]
    self._VerifyValues(tensor_in_sizes=[1, 2, 3, 3],
                       filter_in_sizes=[2, 2, 3, 3],
                       stride=2, padding="VALID",
                       expected=expected_output)

  def testConv2D2x2FilterStride2Same(self):
    expected_output = [2271.0, 2367.0, 2463.0, 1230.0, 1305.0, 1380.0]
    self._VerifyValues(tensor_in_sizes=[1, 2, 3, 3],
                       filter_in_sizes=[2, 2, 3, 3],
                       stride=2, padding="SAME",
                       expected=expected_output)

  # Testing for backprops
  def _RunAndVerifyBackpropInput(self, input_sizes, filter_sizes, output_sizes,
                                 stride, padding, expected, use_gpu):
    total_output_size = 1
    total_filter_size = 1
    for s in output_sizes:
      total_output_size *= s
    for s in filter_sizes:
      total_filter_size *= s
    # Initializes the input tensor with array containing incrementing
    # numbers from 1.
    x1 = [f * 1.0 for f in range(1, total_filter_size + 1)]
    x2 = [f * 1.0 for f in range(1, total_output_size + 1)]
    with self.test_session(use_gpu=use_gpu) as sess:
      t0 = tf.constant(input_sizes, shape=[len(input_sizes)])
      t1 = tf.constant(x1, shape=filter_sizes)
      t2 = tf.constant(x2, shape=output_sizes)
      conv = tf.nn.conv2d_backprop_input(t0, t1, t2,
                                        strides=[1, stride, stride, 1],
                                        padding=padding)
      # "values" consists of two tensors for two backprops
      value = sess.run(conv)
      self.assertShapeEqual(value, conv)
    print "expected = ", expected
    print "actual = ", value
    self.assertArrayNear(expected, value.flatten(), 1e-5)

  def _CompareBackpropInput(self, input_sizes, filter_sizes, output_sizes,
                            stride, padding):
    x1 = np.random.rand(*filter_sizes).astype(np.float32)
    x2 = np.random.rand(*output_sizes).astype(np.float32)
    def _GetVal(use_gpu):
      with self.test_session(use_gpu=use_gpu) as sess:
        t0 = tf.constant(input_sizes, shape=[len(input_sizes)])
        t1 = tf.constant(x1, shape=filter_sizes)
        t2 = tf.constant(x2, shape=output_sizes)
        conv = tf.nn.conv2d_backprop_input(t0, t1, t2,
                                          strides=[1, stride, stride, 1],
                                          padding=padding)
        ret = conv.eval()
        self.assertShapeEqual(ret, conv)
        return ret
    gpu_value = _GetVal(use_gpu=True)
    cpu_value = _GetVal(use_gpu=False)
    self.assertAllClose(cpu_value, gpu_value, rtol=1e-4, atol=1e-4)

  def testConv2D2x2Depth1ValidBackpropInput(self):
    expected_output = [1.0, 4.0, 4.0, 3.0, 10.0, 8.0]
    self._RunAndVerifyBackpropInput(input_sizes=[1, 2, 3, 1],
                                    filter_sizes=[2, 2, 1, 1],
                                    output_sizes=[1, 1, 2, 1],
                                    stride=1, padding="VALID",
                                    expected=expected_output, use_gpu=False)
    self._RunAndVerifyBackpropInput(input_sizes=[1, 2, 3, 1],
                                    filter_sizes=[2, 2, 1, 1],
                                    output_sizes=[1, 1, 2, 1],
                                    stride=1, padding="VALID",
                                    expected=expected_output, use_gpu=True)

  def testConv2D2x2Depth3ValidBackpropInput(self):
    expected_output = [14.0, 32.0, 50.0,
                       100.0, 163.0, 226.0,
                       167.0, 212.0, 257.0,
                       122.0, 140.0, 158.0,
                       478.0, 541.0, 604.0,
                       437.0, 482.0, 527.0]
    self._RunAndVerifyBackpropInput(input_sizes=[1, 2, 3, 3],
                                    filter_sizes=[2, 2, 3, 3],
                                    output_sizes=[1, 1, 2, 3],
                                    stride=1, padding="VALID",
                                    expected=expected_output, use_gpu=False)
    self._RunAndVerifyBackpropInput(input_sizes=[1, 2, 3, 3],
                                    filter_sizes=[2, 2, 3, 3],
                                    output_sizes=[1, 1, 2, 3],
                                    stride=1, padding="VALID",
                                    expected=expected_output, use_gpu=True)

  # Testing for backprops
  def _RunAndVerifyBackpropFilter(self, input_sizes, filter_sizes, output_sizes,
                                  stride, padding, expected, use_gpu):
    total_input_size = 1
    total_output_size = 1
    for s in input_sizes:
      total_input_size *= s
    for s in output_sizes:
      total_output_size *= s
    # Initializes the input tensor with array containing incrementing
    # numbers from 1.
    x0 = [f * 1.0 for f in range(1, total_input_size + 1)]
    x2 = [f * 1.0 for f in range(1, total_output_size + 1)]
    with self.test_session(use_gpu=use_gpu) as sess:
      t0 = tf.constant(x0, shape=input_sizes)
      t1 = tf.constant(filter_sizes, shape=[len(filter_sizes)])
      t2 = tf.constant(x2, shape=output_sizes)
      conv = tf.nn.conv2d_backprop_filter(t0, t1, t2,
                                         strides=[1, stride, stride, 1],
                                         padding=padding)
      value = sess.run(conv)
      self.assertShapeEqual(value, conv)
    print "expected = ", expected
    print "actual = ", value
    self.assertArrayNear(expected, value.flatten(), 1e-5)

  def _CompareBackFilter(self, input_sizes, filter_sizes, output_sizes,
                         stride, padding):
    x0 = np.random.rand(*input_sizes).astype(np.float32)
    x2 = np.random.rand(*output_sizes).astype(np.float32)
    def _GetVal(use_gpu):
      with self.test_session(use_gpu=use_gpu) as sess:
        t0 = tf.constant(x0, shape=input_sizes)
        t1 = tf.constant(filter_sizes, shape=[len(filter_sizes)])
        t2 = tf.constant(x2, shape=output_sizes)
        conv = tf.nn.conv2d_backprop_filter(t0, t1, t2,
                                           strides=[1, stride, stride, 1],
                                           padding=padding)
        ret = conv.eval()
        self.assertShapeEqual(ret, conv)
        return ret
    gpu_value = _GetVal(use_gpu=True)
    cpu_value = _GetVal(use_gpu=False)
    self.assertAllClose(cpu_value, gpu_value, rtol=1e-4, atol=1e-4)

  def testConv2D2x2Depth1ValidBackpropFilter(self):
    expected = [5.0, 8.0, 14.0, 17.0]
    self._RunAndVerifyBackpropFilter(input_sizes=[1, 2, 3, 1],
                                     filter_sizes=[2, 2, 1, 1],
                                     output_sizes=[1, 1, 2, 1],
                                     stride=1, padding="VALID",
                                     expected=expected, use_gpu=False)
    self._RunAndVerifyBackpropFilter(input_sizes=[1, 2, 3, 1],
                                     filter_sizes=[2, 2, 1, 1],
                                     output_sizes=[1, 1, 2, 1],
                                     stride=1, padding="VALID",
                                     expected=expected, use_gpu=True)

  def testConv2D2x2Depth3ValidBackpropFilter(self):
    expected = [17.0, 22.0, 27.0, 22.0, 29.0, 36.0, 27.0, 36.0, 45.0,
                32.0, 43.0, 54.0, 37.0, 50.0, 63.0, 42.0, 57.0, 72.0,
                62.0, 85.0, 108.0, 67.0, 92.0, 117.0, 72.0, 99.0, 126.0,
                77.0, 106.0, 135.0, 82.0, 113.0, 144.0, 87.0, 120.0, 153.0]
    self._RunAndVerifyBackpropFilter(input_sizes=[1, 2, 3, 3],
                                     filter_sizes=[2, 2, 3, 3],
                                     output_sizes=[1, 1, 2, 3],
                                     stride=1, padding="VALID",
                                     expected=expected, use_gpu=False)
    self._RunAndVerifyBackpropFilter(input_sizes=[1, 2, 3, 3],
                                     filter_sizes=[2, 2, 3, 3],
                                     output_sizes=[1, 1, 2, 3],
                                     stride=1, padding="VALID",
                                     expected=expected, use_gpu=True)

  # Gradient checkers
  def ConstructAndTestGradient(self, batch, input_rows, input_cols, filter_rows,
                               filter_cols, in_depth, out_depth, stride,
                               padding, test_input, use_gpu):
    input_shape = [batch, input_rows, input_cols, in_depth]
    filter_shape = [filter_rows, filter_cols, in_depth, out_depth]
    # TODO(yangke): re-factor the computation of output shape.
    if padding == "VALID":
      output_rows = int(math.ceil((input_rows - filter_rows + 1.0) / stride))
      output_cols = int(math.ceil((input_cols - filter_cols + 1.0) / stride))
    else:
      output_rows = int(math.ceil(float(input_rows) / stride))
      output_cols = int(math.ceil(float(input_cols) / stride))
    output_shape = [batch, output_rows, output_cols, out_depth]
    input_size = 1
    for x in input_shape:
      input_size *= x
    filter_size = 1
    for x in filter_shape:
      filter_size *= x
    input_data = [x * 1.0 / input_size for x in range(0, input_size)]
    filter_data = [x * 1.0 / filter_size for x in range(0, filter_size)]
    with self.test_session(use_gpu=use_gpu):
      # Conv2DGrad functions are not compiled for double due to
      # a problem in the way Eigen's Conv2DGrad works for double.
      # So we disable the DOUBLE path.  We should re-enable this
      # when double support returns for CPU and/or GPU.
      # data_type = tf.float64
      # tolerance = 1e-8

      data_type = tf.float32
      tolerance = 0.002

      input_tensor = tf.constant(input_data, shape=input_shape,
                                          dtype=data_type, name="input")
      filter_tensor = tf.constant(filter_data, shape=filter_shape,
                                           dtype=data_type, name="filter")
      conv = tf.nn.conv2d(input_tensor, filter_tensor,
                           [1, stride, stride, 1], padding,
                           name="conv")
      self.assertEqual(output_shape, conv.get_shape())
      if test_input:
        err = gc.ComputeGradientError(input_tensor, input_shape,
                                      conv, output_shape)
      else:
        err = gc.ComputeGradientError(filter_tensor, filter_shape,
                                      conv, output_shape)
      print "conv_2d gradient error = ", err
      self.assertLess(err, tolerance)

  def testInputGradientValidPaddingStrideOne(self):
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=5,
        input_cols=4,
        filter_rows=3,
        filter_cols=3,
        in_depth=2,
        out_depth=3,
        stride=1,
        padding="VALID",
        test_input=True,
        use_gpu=False)
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=5,
        input_cols=4,
        filter_rows=3,
        filter_cols=3,
        in_depth=2,
        out_depth=3,
        stride=1,
        padding="VALID",
        test_input=True,
        use_gpu=True)

  def testFilterGradientValidPaddingStrideOne(self):
    self.ConstructAndTestGradient(
        batch=4,
        input_rows=6,
        input_cols=5,
        filter_rows=2,
        filter_cols=2,
        in_depth=2,
        out_depth=3,
        stride=1,
        padding="VALID",
        test_input=False,
        use_gpu=False)
    self.ConstructAndTestGradient(
        batch=4,
        input_rows=6,
        input_cols=5,
        filter_rows=2,
        filter_cols=2,
        in_depth=2,
        out_depth=3,
        stride=1,
        padding="VALID",
        test_input=False,
        use_gpu=True)

  def testInputGradientValidPaddingStrideTwo(self):
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=4,
        input_cols=5,
        filter_rows=3,
        filter_cols=3,
        in_depth=2,
        out_depth=3,
        stride=2,
        padding="VALID",
        test_input=True,
        use_gpu=False)
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=4,
        input_cols=5,
        filter_rows=3,
        filter_cols=3,
        in_depth=2,
        out_depth=3,
        stride=2,
        padding="VALID",
        test_input=True,
        use_gpu=True)

  def testFilterGradientValidPaddingStrideTwo(self):
    self.ConstructAndTestGradient(
        batch=4,
        input_rows=6,
        input_cols=5,
        filter_rows=2,
        filter_cols=2,
        in_depth=2,
        out_depth=3,
        stride=2,
        padding="VALID",
        test_input=False,
        use_gpu=False)
    self.ConstructAndTestGradient(
        batch=4,
        input_rows=6,
        input_cols=5,
        filter_rows=2,
        filter_cols=2,
        in_depth=2,
        out_depth=3,
        stride=2,
        padding="VALID",
        test_input=False,
        use_gpu=True)

  def testInputGradientValidPaddingStrideThree(self):
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=7,
        input_cols=6,
        filter_rows=3,
        filter_cols=3,
        in_depth=4,
        out_depth=5,
        stride=3,
        padding="VALID",
        test_input=True,
        use_gpu=False)
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=7,
        input_cols=6,
        filter_rows=3,
        filter_cols=3,
        in_depth=4,
        out_depth=5,
        stride=3,
        padding="VALID",
        test_input=True,
        use_gpu=True)

  def testFilterGradientValidPaddingStrideThree(self):
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=8,
        input_cols=7,
        filter_rows=4,
        filter_cols=4,
        in_depth=2,
        out_depth=3,
        stride=3,
        padding="VALID",
        test_input=False,
        use_gpu=False)
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=8,
        input_cols=7,
        filter_rows=4,
        filter_cols=4,
        in_depth=2,
        out_depth=3,
        stride=3,
        padding="VALID",
        test_input=False,
        use_gpu=True)

  def testInputGradientSamePaddingStrideOne(self):
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=7,
        input_cols=6,
        filter_rows=3,
        filter_cols=3,
        in_depth=2,
        out_depth=3,
        stride=1,
        padding="SAME",
        test_input=True,
        use_gpu=False)
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=7,
        input_cols=6,
        filter_rows=3,
        filter_cols=3,
        in_depth=2,
        out_depth=3,
        stride=1,
        padding="SAME",
        test_input=True,
        use_gpu=True)

  def testFilterGradientSamePaddingStrideOne(self):
    self.ConstructAndTestGradient(
        batch=4,
        input_rows=6,
        input_cols=5,
        filter_rows=2,
        filter_cols=2,
        in_depth=2,
        out_depth=3,
        stride=1,
        padding="SAME",
        test_input=False,
        use_gpu=False)
    self.ConstructAndTestGradient(
        batch=4,
        input_rows=6,
        input_cols=5,
        filter_rows=2,
        filter_cols=2,
        in_depth=2,
        out_depth=3,
        stride=1,
        padding="SAME",
        test_input=False,
        use_gpu=True)

  def testInputGradientSamePaddingStrideTwo(self):
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=5,
        input_cols=4,
        filter_rows=3,
        filter_cols=3,
        in_depth=3,
        out_depth=3,
        stride=2,
        padding="SAME",
        test_input=True,
        use_gpu=False)
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=5,
        input_cols=4,
        filter_rows=3,
        filter_cols=3,
        in_depth=3,
        out_depth=3,
        stride=2,
        padding="SAME",
        test_input=True,
        use_gpu=True)

  def testFilterGradientSamePaddingStrideTwo(self):
    self.ConstructAndTestGradient(
        batch=4,
        input_rows=6,
        input_cols=5,
        filter_rows=2,
        filter_cols=2,
        in_depth=2,
        out_depth=3,
        stride=2,
        padding="SAME",
        test_input=False,
        use_gpu=False)
    self.ConstructAndTestGradient(
        batch=4,
        input_rows=6,
        input_cols=5,
        filter_rows=2,
        filter_cols=2,
        in_depth=2,
        out_depth=3,
        stride=2,
        padding="SAME",
        test_input=False,
        use_gpu=True)

  def testInputGradientSamePaddingStrideThree(self):
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=7,
        input_cols=6,
        filter_rows=3,
        filter_cols=3,
        in_depth=4,
        out_depth=5,
        stride=3,
        padding="SAME",
        test_input=True,
        use_gpu=False)
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=7,
        input_cols=6,
        filter_rows=3,
        filter_cols=3,
        in_depth=4,
        out_depth=5,
        stride=3,
        padding="SAME",
        test_input=True,
        use_gpu=True)

  def testFilterGradientSamePaddingStrideThree(self):
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=8,
        input_cols=7,
        filter_rows=4,
        filter_cols=4,
        in_depth=2,
        out_depth=3,
        stride=3,
        padding="SAME",
        test_input=False,
        use_gpu=False)
    self.ConstructAndTestGradient(
        batch=2,
        input_rows=8,
        input_cols=7,
        filter_rows=4,
        filter_cols=4,
        in_depth=2,
        out_depth=3,
        stride=3,
        padding="SAME",
        test_input=False,
        use_gpu=True)

  def testShapeFunctionEdgeCases(self):
    # All shapes unknown.
    c1 = tf.nn.conv2d(tf.placeholder(tf.float32),
                       tf.placeholder(tf.float32),
                       strides=[1, 1, 1, 1], padding="SAME")
    self.assertEqual([None, None, None, None], c1.get_shape().as_list())

    # Incorrect input shape.
    with self.assertRaises(ValueError):
      tf.nn.conv2d(tf.placeholder(tf.float32, shape=[1, 3]),
                    tf.placeholder(tf.float32),
                    strides=[1, 1, 1, 1], padding="SAME")

    # Incorrect filter shape.
    with self.assertRaises(ValueError):
      tf.nn.conv2d(tf.placeholder(tf.float32),
                    tf.placeholder(tf.float32, shape=[1, 3]),
                    strides=[1, 1, 1, 1], padding="SAME")

    # Depth mismatch.
    with self.assertRaises(ValueError):
      tf.nn.conv2d(tf.placeholder(tf.float32,
                                          shape=[32, 20, 20, 3]),
                    tf.placeholder(tf.float32,
                                          shape=[4, 4, 2, 2]),
                    strides=[1, 1, 1, 1], padding="SAME")

    # Illegal strides.
    with self.assertRaisesRegexp(ValueError, "strides in the batch and depth"):
      tf.nn.conv2d(tf.placeholder(tf.float32),
                    tf.placeholder(tf.float32),
                    strides=[2, 1, 1, 1], padding="SAME")
    with self.assertRaisesRegexp(ValueError, "strides in the batch and depth"):
      tf.nn.conv2d(tf.placeholder(tf.float32),
                    tf.placeholder(tf.float32),
                    strides=[1, 1, 1, 2], padding="SAME")

    # Filter larger than input.
    with self.assertRaisesRegexp(ValueError,
                                 "filter must not be larger than the input"):
      tf.nn.conv2d(tf.placeholder(tf.float32,
                                          shape=[32, 20, 20, 3]),
                    tf.placeholder(tf.float32,
                                          shape=[20, 21, 3, 2]),
                    strides=[1, 1, 1, 1], padding="SAME")
    with self.assertRaisesRegexp(ValueError,
                                 "filter must not be larger than the input"):
      tf.nn.conv2d(tf.placeholder(tf.float32,
                                          shape=[32, 20, 20, 3]),
                    tf.placeholder(tf.float32,
                                          shape=[21, 20, 3, 2]),
                    strides=[1, 1, 1, 1], padding="SAME")

    # Stride larger than filter.
    with self.assertRaisesRegexp(ValueError,
                                 "stride must be less than or equal to filter"):
      tf.nn.conv2d(tf.placeholder(tf.float32,
                                          shape=[32, 20, 20, 3]),
                    tf.placeholder(tf.float32,
                                          shape=[4, 5, 3, 2]),
                    strides=[1, 5, 5, 1], padding="SAME")
    with self.assertRaisesRegexp(ValueError,
                                 "stride must be less than or equal to filter"):
      tf.nn.conv2d(tf.placeholder(tf.float32,
                                          shape=[32, 20, 20, 3]),
                    tf.placeholder(tf.float32,
                                          shape=[5, 4, 3, 2]),
                    strides=[1, 5, 5, 1], padding="SAME")

    # Invalid rectangular stride.
    with self.assertRaisesRegexp(ValueError,
                                 "equal length strides in the row and column"):
      tf.nn.conv2d(tf.placeholder(tf.float32),
                    tf.placeholder(tf.float32),
                    strides=[1, 3, 7, 1], padding="SAME")


# This is only a very simple test. More comprehensive tests live in
# //learning/dist_belief/experimental/brain_compatibility/conv_nn_test.py
# where we compare the numeric results of the depthwise conv op with the
# depthwise weighted sum transformer in dist_belief.
class DepthwiseConv2DTest(tf.test.TestCase):

  def _VerifyValues(self, tensor_in_sizes, filter_in_sizes, stride,
                    padding, expected):
    """Verifies the output values of the convolution function.

    Args:
      tensor_in_sizes: Input tensor dimensions in
        [batch, input_rows, input_cols, input_depth].
      filter_in_sizes: Filter tensor dimensions in
        [filter_rows, filter_cols, input_depth, depth_multiplier].
      stride: Stride.
      padding: Padding type.
      expected: An array containing the expected operation outputs.
    """
    total_size_1 = 1
    total_size_2 = 1
    for s in tensor_in_sizes:
      total_size_1 *= s
    for s in filter_in_sizes:
      total_size_2 *= s
    # Initializes the input tensor with array containing incrementing
    # numbers from 1.
    x1 = [f * 1.0 for f in range(1, total_size_1 + 1)]
    x2 = [f * 1.0 for f in range(1, total_size_2 + 1)]
    with self.test_session() as sess:
      t1 = tf.constant(x1, shape=tensor_in_sizes)
      t1.set_shape(tensor_in_sizes)
      t2 = tf.constant(x2, shape=filter_in_sizes)
      conv = tf.nn.depthwise_conv2d(t1, t2, strides=[1, stride, stride, 1],
                                    padding=padding)
      value = sess.run(conv)
    print "value = ", value
    self.assertArrayNear(expected, np.ravel(value), 1e-5)
    self.assertShapeEqual(value, conv)

  def testConv2D2x2Filter(self):
    # The inputs look like this (it's a 3 x 2 matrix, each of depth 2):
    #
    # [ (1.0, 2.0), (3.0,  4.0), ( 5.0,  6.0) ]
    # [ (7.0, 8.0), (9.0, 10.0), (11.0, 12.0) ]
    #  We can view this as two inputs
    #
    #  input depth 0:
    #
    #  [ 1.0,  3.0,  5.0 ]
    #  [ 7.0,  9.0, 11.0 ]
    #
    #  input depth 1:
    #
    #  [ 2.0,  4.0,  6.0 ]
    #  [ 8.0, 10.0, 12.0 ]
    #
    # The filter looks like this (it has two 2 x 2 patches, each generating 2
    # depths):
    #
    #  filter #0:
    #
    #  [ (1.0,  3.0), ( 5.0,  7.0)]
    #  [ (9.0, 11.0), (13.0, 15.0)]
    #
    #  filter #1:
    #
    #  [ ( 2.0,  4.0), ( 6.0,  8.0)]
    #  [ (10.0, 12.0), (14.0, 16.0)]
    #
    # So the outputs are:
    #
    # (position 0, 0: in_depth 0, output_depth 0 -- using filter #0)
    #  1.0 * 1.0 + 7.0 * 9.0 + 3.0 * 5.0 + 9.0 * 13.0 = 196
    # (position 0, 0: in_depth 0, output_depth 1 -- using filter #1)
    #  1.0 * 2.0 + 7.0 * 10.0 + 3.0 * 6.0 + 9.0 * 14.0 = 216
    # (position 0, 0: in_depth 1, output_depth 2 -- using filter #0)
    #  2.0 * 3.0 + 8.0 * 11.0 + 4.0 * 7.0 + 10.0 * 15.0 = 272
    # (position 0, 0: in_depth 1, output_depth 3 -- using filter #1)
    #  2.0 * 4.0 + 8.0 * 12.0 + 4.0 * 8.0 + 10.0 * 16.0 = 296
    #
    # (position 1, 0: in_depth 0, output_depth 0 -- using filter #0)
    #  3.0 * 1.0 + 9.0 * 9.0 + 5.0 * 5.0 + 11.0 * 13.0 = 252
    # (position 1, 0: in_depth 0, output_depth 1 -- using filter #1)
    #  3.0 * 2.0 + 9.0 * 10.0 + 5.0 * 6.0 + 11.0 * 14.0 = 280
    # (position 1, 0: in_depth 1, output_depth 2 -- using filter #0)
    #  4.0 * 3.0 + 10.0 * 11.0 + 6.0 * 7.0 + 12.0 * 15.0 = 344
    # (position 1, 0: in_depth 1, output_depth 3 -- using filter #1)
    #  4.0 * 4.0 + 10.0 * 12.0 + 6.0 * 8.0 + 12.0 * 16.0 = 376
    expected_output = [196, 216, 272, 296, 252, 280, 344, 376]
    self._VerifyValues(tensor_in_sizes=[1, 2, 3, 2],
                       filter_in_sizes=[2, 2, 2, 2],
                       stride=1, padding="VALID",
                       expected=expected_output)


class SeparableConv2DTest(tf.test.TestCase):

  def _InitValues(self, sizes):
    """Initializes values for input tensors.

    Args:
      sizes: Tensor dimensions.

    Returns:
      Tensor initialized to values.
    """
    total_size = 1
    for s in sizes:
      total_size *= s
    x = [f * 0.5 for f in range(1, total_size + 1)]
    return tf.constant(x, shape=sizes)

  def _VerifyValues(self, tensor_in_sizes, depthwise_filter_in_sizes,
                    pointwise_filter_in_sizes, stride, padding, expected):
    """Verifies the output values of the separable convolution function.

    Args:
      tensor_in_sizes: Input tensor dimensions.
      depthwise_filter_in_sizes: Depthwise filter tensor dimensions.
      pointwise_filter_in_sizes: Pointwise filter tensor dimensions.
      stride: Stride.
      padding: Padding type.
      expected: An array containing the expected operation outputs.
    """
    with self.test_session() as sess:
      t1 = self._InitValues(tensor_in_sizes)
      f1 = self._InitValues(depthwise_filter_in_sizes)
      f1.set_shape(depthwise_filter_in_sizes)
      f2 = self._InitValues(pointwise_filter_in_sizes)
      conv = tf.nn.separable_conv2d(t1, f1, f2, strides=[1, stride, stride, 1],
                                    padding=padding)
      value = sess.run(conv)
    print "value = ", value
    self.assertArrayNear(expected, np.ravel(value), 1e-5)
    self.assertShapeEqual(value, conv)

  def testSeparableConv2D(self):
    # The output is the result of two convolutions:
    # First with tensor_in[1, 4, 4, 3] * filter1[2, 2, 3, 3].
    # Second with intermediate_out[4, 4, 3, 3] * filter2[1, 1, 3, 6].
    # Complexity is O(3*3*2*2 + 3*6*1*1] as opposed to O(3*6*2*2).
    expected_output = [
        6644.5, 6971.5, 7298.5, 7625.5, 7952.5, 8279.5, 8606.5, 8154.5, 8556.5,
        8958.5, 9360.5, 9762.5, 10164.5, 10566.5, 9664.5, 10141.5, 10618.5,
        11095.5, 11572.5, 12049.5, 12526.5, 4145.5, 4346.5, 4547.5, 4748.5,
        4949.5, 5150.5, 5351.5, 12684.5, 13311.5, 13938.5, 14565.5, 15192.5,
        15819.5, 16446.5, 14194.5, 14896.5, 15598.5, 16300.5, 17002.5, 17704.5,
        18406.5, 15704.5, 16481.5, 17258.5, 18035.5, 18812.5, 19589.5, 20366.5,
        6499.5, 6814.5, 7129.5, 7444.5, 7759.5, 8074.5, 8389.5, 18724.5,
        19651.5, 20578.5, 21505.5, 22432.5, 23359.5, 24286.5, 20234.5, 21236.5,
        22238.5, 23240.5, 24242.5, 25244.5, 26246.5, 21744.5, 22821.5, 23898.5,
        24975.5, 26052.5, 27129.5, 28206.5, 8853.5, 9282.5, 9711.5, 10140.5,
        10569.5, 10998.5, 11427.5, 5746.75, 6010.75, 6274.75, 6538.75, 6802.75,
        7066.75, 7330.75, 6168.75, 6452.25, 6735.75, 7019.25, 7302.75, 7586.25,
        7869.75, 6590.75, 6893.75, 7196.75, 7499.75, 7802.75, 8105.75, 8408.75,
        2036.25, 2119.5, 2202.75, 2286.0, 2369.25, 2452.5, 2535.75]

    self._VerifyValues(tensor_in_sizes=[1, 4, 4, 2],
                       depthwise_filter_in_sizes=[2, 2, 2, 3],
                       pointwise_filter_in_sizes=[1, 1, 6, 7],
                       stride=1, padding="SAME",
                       expected=expected_output)


def GetInceptionFwdTest(input_size, filter_size, stride, padding):
  def Test(self):
    tf.logging.info("Testing InceptionFwd %s", (input_size, filter_size,
                                                stride, padding))
    self._CompareFwdValues(input_size, filter_size, stride, padding)
  return Test


def GetInceptionBackInputTest(input_size, filter_size, output_size,
                              stride, padding):
  def Test(self):
    tf.logging.info("Testing InceptionBackInput %s",
                    (input_size, filter_size, output_size, stride, padding))
    self._CompareBackpropInput(input_size, filter_size, output_size,
                               stride, padding)
  return Test


def GetInceptionBackFilterTest(input_size, filter_size, output_size,
                               stride, padding):
  def Test(self):
    tf.logging.info("Testing InceptionBackFilter %s",
                    (input_size, filter_size, output_size, stride, padding))
    self._CompareBackFilter(input_size, filter_size, output_size,
                            stride, padding)
  return Test


if __name__ == "__main__":
  for index, (input_size_, filter_size_, output_size_, stride_,
              padding_) in enumerate(GetInceptionShapes()):
    setattr(Conv2DTest, "testInceptionFwd_" + str(index),
            GetInceptionFwdTest(input_size_, filter_size_, stride_, padding_))
    setattr(Conv2DTest, "testInceptionBackInput_" + str(index),
            GetInceptionBackInputTest(input_size_, filter_size_, output_size_,
                                      stride_, padding_))
    setattr(Conv2DTest, "testInceptionBackFilter_" + str(index),
            GetInceptionBackFilterTest(input_size_, filter_size_, output_size_,
                                       stride_, padding_))
  tf.test.main()
