# coding=utf-8
import tensorflow as tf

from tf_geometric.nn.kernel.map_reduce import aggregate_neighbors, sum_updater, sum_reducer, identity_updater
from tf_geometric.utils.graph_utils import add_self_loop_edge


def gcn_norm_edge(edge_index, num_nodes, edge_weight=None, improved=False, cache=None):
    cache_key = "gcn_normed_edge"

    if cache is not None and cache_key in cache and cache[cache_key] is not None:
        return cache[cache_key]


    if edge_weight is None:
        edge_weight = tf.ones([edge_index.shape[1]], dtype=tf.float32)

    fill_weight = 2.0 if improved else 1.0
    edge_index, edge_weight = add_self_loop_edge(edge_index, num_nodes, edge_weight=edge_weight, fill_weight=fill_weight)

    row, col = edge_index
    deg = tf.math.unsorted_segment_sum(edge_weight, row, num_segments=num_nodes)
    deg_inv_sqrt = tf.pow(deg, -0.5)
    deg_inv_sqrt = tf.where(tf.math.is_inf(deg_inv_sqrt), tf.zeros_like(deg_inv_sqrt), deg_inv_sqrt)
    deg_inv_sqrt = tf.where(tf.math.is_nan(deg_inv_sqrt), tf.zeros_like(deg_inv_sqrt), deg_inv_sqrt)

    noremd_edge_weight = tf.gather(deg_inv_sqrt, row) * edge_weight * tf.gather(deg_inv_sqrt, col)

    if cache is not None:
        cache[cache_key] = edge_index, noremd_edge_weight

    return edge_index, noremd_edge_weight


def gcn_mapper(repeated_x, neighbor_x, edge_weight=None):
    return neighbor_x * tf.expand_dims(edge_weight, 1)


def gcn(x, edge_index, edge_weight, kernel, bias=None, activation=None, improved=False, cache=None):
    updated_edge_index, normed_edge_weight = gcn_norm_edge(edge_index, x.shape[0], edge_weight,
                                                           improved, cache)
    x = x @ kernel
    h = aggregate_neighbors(
        x, updated_edge_index, normed_edge_weight,
        gcn_mapper,
        sum_reducer,
        identity_updater
    )

    if bias is not None:
        h += bias

    if activation is not None:
        h = activation(h)

    return h


# def norm_and_gcn(x, edge_index, num_nodes, dense_w, edge_weight=None, dense_b=None, activation=None):
#     updated_edge_index, normed_edge_weight = gcn_norm_edge(edge_index, num_nodes, edge_weight)
#     outputs = gcn(x, updated_edge_index, normed_edge_weight, dense_w, dense_b, activation)
#     return outputs




