# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

import json, os, math
from collections import defaultdict

"""
Utilities for working with function program representations of questions.

Some of the metadata about what question node types are available etc are stored
in a JSON metadata file.
"""


# Handlers for answering questions. Each handler receives the scene structure
# that was output_doc_info from Blender, the node, and a list of values that were output_doc_info
# from each of the node's inputs; the handler should return the computed output_doc_info
# value from this node.

def all_scene_handler(all_scene, doc_metadata, inputs, side_inputs):
    # Just return all objects in the scene
    return list(range(len(all_scene['objects'])))


def metadata_handler(all_scene, doc_metadata, inputs, side_inputs):
    return list(range(len(doc_metadata.keys())))


def make_filter_handler(attribute):
    def filter_handler(all_scene, doc_metadata, inputs, side_inputs):
        value = side_inputs[0]
        output = []
        for idx in inputs[0]:
            atr = all_scene['objects'][idx][attribute]
            if value == str(atr):
                output.append(idx)
        return output

    return filter_handler


def make_filter_list_handler(attribute):
    def filter_handler(all_scene, doc_metadata, inputs, side_inputs):
        values = inputs[0]
        output = ""
        for value in values:
            # !!! assume the idx is the segment_id
            output += all_scene[value]['text']
        return output

    return filter_handler


def count_handler(all_scene, doc_metadata, inputs, side_inputs):
    assert len(inputs) == 1
    return len(inputs[0])


def count_larger_zero_handler(all_scene, doc_metadata, inputs, side_inputs):
    assert len(inputs) == 1
    _len = len(inputs[0])
    return _len if 0 < _len <= 5 else '__INVALID__'


def make_query_metadata_handler(all_scene, doc_metadata, inputs, side_inputs):
    key = side_inputs[0]
    if key not in doc_metadata.keys():
        return '__INVALID__'
    val = doc_metadata[key]
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        return list(val.keys())
    return str(val)


def make_query_handler(attributes, recursion=1):
    def query_handler(all_scene, doc_metadata, inputs, side_inputs):
        if len(inputs[0]) != 1:
            return "__INVALID__"
        key = int(inputs[0][0])
        target = all_scene['objects'][key]

        curr = target
        for i in range(recursion):
            if attributes[i] not in curr.keys():
                return "__INVALID__"
            curr = curr[attributes[i]]
            if attributes[i] == 'text' and curr == '':
                return "__INVALID__"
        return curr

    return query_handler


def exist_handler(all_scene, doc_metadata, inputs, side_inputs):
    assert len(inputs) == 1
    assert len(side_inputs) == 0
    return len(inputs[0]) > 0


def unique_handler(all_scene, doc_metadata, inputs, side_inputs):
    assert len(inputs) == 1
    if len(inputs[0]) != 1:
        return '__INVALID__'
    return inputs[0][0]


def query_relation_handler(relation):
    def query_handler(all_scene, doc_metadata, inputs, side_inputs):
        # available_category = ['title', 'figure caption', 'table caption']
        val = inputs[0]
        obj = all_scene['objects'][val]
        nodes = obj['parent_child_relations']
        res = []
        for node in nodes:
            if node[0] == relation:
                return [node[1]]
        return '__INVALID__'

    return query_handler


def make_position_query_handler(all_scene, doc_metadata, inputs, side_inputs):
    pos_dict = {'top': 'bottom', 'bottom': 'top', 'left': 'right', 'right': 'left'}
    val = inputs[0]
    # obj = all_scene[val]
    position = pos_dict[side_inputs[0]]
    return all_scene['relations'][position][val]


def compare_position_handler(all_scene, doc_metadata, inputs, side_inputs):
    obj1, obj2 = inputs
    page = all_scene[obj1]['page_number']


def filter_second_handler(attribute, filter_steps=[]):
    def filter_handler(all_scene, doc_metadata, inputs, side_inputs):
        assert attribute == "category_id"
        value = side_inputs[0]
        output = []
        src, first_stage_elements = inputs
        page = all_scene[first_stage_elements]['page_number']
        for filter_step in filter_steps:
            key, value = filter_step
            for idx in inputs[0]:
                atr = all_scene[idx][attribute]
                if value == str(atr):
                    output.append(idx)
        return output


def list_to_string(all_scene, doc_metadata, inputs, side_inputs):
    val = inputs[0]
    if isinstance(val, list):
        return ";".join(val)
    return val


def make_segment_id_query_handler(attribute):
    def make_query(all_scene, doc_metadata, inputs, side_inputs):
        key = inputs[0]
        target = None
        for i, scene in all_scene.items():
            if scene['segment_id'] == key:
                target = scene
                break
        if target is None:
            return '__INVALID__'
        if attribute not in target.keys():
            return "__INVALID__"
        return target[attribute]

    return make_query


def attr_exist_handler(attribute):
    def exist_handler(all_scene, doc_metadata, inputs, side_inputs):
        for key in inputs[0]:
            target = all_scene['objects'][int(key)]
            if target['category_id'].endswith(attribute):
                return True
        return False

    return exist_handler


def make_segment_id_filter_handler(attribute):
    def make_filter(all_scene, doc_metadata, inputs, side_inputs):
        values = inputs[0]
        if len(values) == 0:
            return '__INVALID__'
        category = side_inputs[0]
        output = []
        for i, scene in all_scene.items():
            if scene['segment_id'] in values and scene['category_id'] == category:
                output.append(scene['segment_id'])
        return output

    return make_filter


def query_segment_id_relation_handler(relation):
    def query_handler(all_scene, doc_metadata, inputs, side_inputs):
        # available_category = ['title', 'figure caption', 'table caption']
        value = inputs[0]
        for i, scene in all_scene.items():
            if scene['segment_id'] != value:
                continue
            if relation not in scene.keys():
                return '__INVALID__'
            nodes = scene[relation]
            break
        if isinstance(nodes, list) and len(nodes) == 0:
            return '__INVALID__'
        if isinstance(nodes, str) and nodes == "":
            return '__INVALID__'
        return nodes

    return query_handler


def query_child_position(obj_category):
    def query_handler(all_scene, doc_metadata, inputs, side_inputs):
        anti_pos = {'top': 'bottom', 'bottom': 'top'}
        caption = None
        val = inputs[0]
        obj = all_scene['objects'][val]
        nodes = obj['parent_child_relations']
        res = []
        for node in nodes:
            if node[0] == 'parent':
                res.append(node[1])
        for key in res:
            target = all_scene['objects'][int(key)]
            if target['category_id'].endswith(obj_category):
                caption = target['local_id']
        if not caption:
            return '__INVALID__'
        for pos in ['top', 'bottom']:
            if caption in all_scene['relations'][pos][val]:
                return anti_pos[pos]
        return '__INVALID__'

    return query_handler


# Register all of the answering handlers here.
# care of registration? Not sure. Also what if we want to reuse the same engine
# for different sets of node types?
execute_handlers = {
    'all_scene': all_scene_handler,
    'metadata': metadata_handler,
    'filter_category': make_filter_handler('category_id'),
    'filter_index': make_filter_handler('local_id'),
    'filter_section': make_filter_handler('section'),
    'filter_list_text': make_filter_list_handler('text'),
    'filter_element': make_filter_handler('category_id'),
    'filter_page': make_filter_handler('page_number'),
    'filter_category_via_segment_id': make_segment_id_filter_handler('category_id'),
    'count': count_handler,
    'count_larger_zero': count_larger_zero_handler,
    'query_metadata_attr': make_query_metadata_handler,
    'query_page': make_query_handler(['page_number']),
    'query_category': make_query_handler(['category_id']),
    'query_caption': make_query_handler(['caption']),
    'query_text': make_query_handler(['text']),
    'query_text_via_segment_id': make_segment_id_query_handler('text'),
    'query_category_via_segment_id': make_segment_id_query_handler('category_id'),
    'query_position': make_position_query_handler,
    'exist': exist_handler,
    'caption_exist': attr_exist_handler('caption'),
    'caption_position': query_child_position('caption'),
    'unique': unique_handler,
    'query_children': query_relation_handler('child'),
    'query_parent': query_relation_handler('parent'),
    'query_children_via_segment_id': query_segment_id_relation_handler('child'),
    'compare_position': compare_position_handler,
    'filter_second_elements': filter_second_handler('category_id'),
    'to_string': list_to_string
}


def answer_question(question, doc_metadata, all_scene, all_outputs=False,
                    cache_outputs=True):
    """
    Use structured scene information to answer a structured question. Most of the
    heavy lifting is done by the execute handlers defined above.

    We cache node outputs in the node itself; this gives a nontrivial speedup
    when we want to answer many questions that share nodes on the same scene
    (such as during question-generation DFS). This will NOT work if the same
    nodes are executed on different scenes.
    """
    # special_methods may not need to access the info from scene
    node_outputs = []
    for node in question['nodes']:
        if cache_outputs and '_output' in node:
            node_output = node['_output']
        else:
            node_type = node['type']
            msg = 'Could not find handler for "%s"' % node_type
            assert node_type in execute_handlers, msg
            handler = execute_handlers[node_type]
            node_inputs = [node_outputs[idx] for idx in node['inputs']]
            side_inputs = node.get('side_inputs', [])
            node_output = handler(all_scene, doc_metadata, node_inputs, side_inputs)
            if cache_outputs:
                node['_output'] = node_output
        node_outputs.append(node_output)
        if node_output == '__INVALID__':
            break

    if all_outputs:
        return node_outputs
    else:
        return node_outputs[-1]


def insert_scene_node(nodes, idx):
    # First make a shallow-ish copy of the input
    new_nodes = []
    for node in nodes:
        new_node = {
            'type': node['type'],
            'inputs': node['inputs'],
        }
        if 'side_inputs' in node:
            new_node['side_inputs'] = node['side_inputs']
        new_nodes.append(new_node)

    # Replace the specified index with a scene node
    new_nodes[idx] = {'type': 'scene', 'inputs': []}

    # Search backwards from the last node to see which nodes are actually used
    output_used = [False] * len(new_nodes)
    idxs_to_check = [len(new_nodes) - 1]
    while idxs_to_check:
        cur_idx = idxs_to_check.pop()
        output_used[cur_idx] = True
        idxs_to_check.extend(new_nodes[cur_idx]['inputs'])

    # Iterate through nodes, keeping only those whose output_doc_info is used;
    # at the same time build up a mapping from old idxs to new idxs
    old_idx_to_new_idx = {}
    new_nodes_trimmed = []
    for old_idx, node in enumerate(new_nodes):
        if output_used[old_idx]:
            new_idx = len(new_nodes_trimmed)
            new_nodes_trimmed.append(node)
            old_idx_to_new_idx[old_idx] = new_idx

    # Finally go through the list of trimmed nodes and change the inputs
    for node in new_nodes_trimmed:
        new_inputs = []
        for old_idx in node['inputs']:
            new_inputs.append(old_idx_to_new_idx[old_idx])
        node['inputs'] = new_inputs

    return new_nodes_trimmed
