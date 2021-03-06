# coding=utf-8
import tensorflow as tf

from tf_geometric.nn.conv.gat import gat
from tf_geometric.layers.kernel.map_reduce import MapReduceGNN


class GAT(MapReduceGNN):

    def __init__(self, units,
                 attention_units=None,
                 activation=None,
                 num_heads=1,
                 query_activation=tf.nn.relu,
                 key_activation=tf.nn.relu,
                 drop_rate=0.0,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.units = units
        self.attention_units = units if attention_units is None else attention_units
        self.drop_rate = drop_rate

        self.query_kernel = None
        self.query_bias = None
        self.query_activation = query_activation

        self.key_kernel = None
        self.key_bias = None
        self.key_activation = key_activation

        self.kernel = None
        self.bias = None

        self.acvitation = activation
        self.num_heads = num_heads

    def build(self, input_shapes):
        x_shape = input_shapes[0]
        num_features = x_shape[-1]

        self.query_kernel = self.add_weight("query_kernel", shape=[num_features, self.attention_units], initializer="glorot_uniform")
        self.query_bias = self.add_weight("query_bias", shape=[self.attention_units], initializer="zeros")

        self.key_kernel = self.add_weight("key_kernel", shape=[num_features, self.attention_units], initializer="glorot_uniform")
        self.key_bias = self.add_weight("key_bias", shape=[self.attention_units], initializer="zeros")

        self.kernel = self.add_weight("kernel", shape=[num_features, self.units], initializer="glorot_uniform")
        self.bias = self.add_weight("bias", shape=[self.units], initializer="zeros")

    def call(self, inputs, training=None, mask=None):
        x, edge_index = inputs

        return gat(x, edge_index,
                   self.query_kernel, self.query_bias, self.query_activation,
                   self.key_kernel, self.key_bias, self.key_activation,
                   self.kernel, self.bias, self.acvitation,
                   num_heads=self.num_heads,
                   drop_rate=self.drop_rate,
                   training=training)