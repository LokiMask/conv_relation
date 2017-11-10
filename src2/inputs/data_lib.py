# Copyright 2017 Google Inc. All Rights Reserved.
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
# ==============================================================================
"""Create TFRecord files of SequenceExample protos from dataset.

Constructs 3 datasets:
  1. Labeled data for the LSTM classification model.
     "*_cl.tfrecords" (for both unidirectional and bidirectional
     models).
  2. Data for the unsupervised LM-LSTM model that predicts the next token.
     "*_lm.tfrecords" (generates forward and reverse data).
  3. Data for the unsupervised SA-LSTM model that uses Seq2Seq.
     "*_sa.tfrecords".
"""

import os
import string

# Dependency imports

import tensorflow as tf
from inputs import tfrecords as data
# from adversarial_text.data import data_utils
# from adversarial_text.data import document_generators

# Data filenames
# Sequence Autoencoder
ALL_SA = 'all_sa.tfrecords'
TRAIN_SA = 'train_sa.tfrecords'
TEST_SA = 'test_sa.tfrecords'
# Language Model
ALL_LM = 'all_lm.tfrecords'
TRAIN_LM = 'train_lm.tfrecords'
TEST_LM = 'test_lm.tfrecords'
# Classification
TRAIN_CLASS = 'train_cl.tfrecords'
TEST_CLASS = 'test_cl.tfrecords'
# LM with bidirectional LSTM
TRAIN_REV_LM = 'train_reverse_lm.tfrecords'
TEST_REV_LM = 'test_reverse_lm.tfrecords'
# Classification with bidirectional LSTM
TRAIN_BD_CLASS = 'train_bidir_cl.tfrecords'
TEST_BD_CLASS = 'test_bidir_cl.tfrecords'


# data = data_utils
flags = tf.app.flags
FLAGS = flags.FLAGS

# Flags for input data are in document_generators.py
# flags.DEFINE_string('vocab_file', '', 'Path to the vocabulary file. Defaults '
#                     'to FLAGS.output_dir/vocab.txt.')
# flags.DEFINE_string('output_dir', '', 'Path to save tfrecords.')

# # Config
# flags.DEFINE_boolean('label_gain', False,
#                      'Enable linear label gain. If True, sentiment label will '
#                      'be included at each timestep with linear weight '
#                      'increase.')


def _writer(fname):
  '''wrapper of writer ot deal with relative path'''
  path = os.path.join(FLAGS.data_dir, fname)
  return tf.python_io.TFRecordWriter(path)

def _shuff_writer(fname):
  '''wrapper of writer ot deal with relative path'''
  path = os.path.join(FLAGS.data_dir, fname)
  return ShufflingTFRecordWriter(path)


def _build_input_sequence(raw_example, vocab_ids):
  """Builds input sequence from raw_example.

  PositionPair = namedtuple('PosPair', 'first last')
  Raw_Example = namedtuple('Raw_Example', 'label entity1 entity2 sentence')

  Terms are added as token in the SequenceExample.  The EOS_TOKEN is also
  appended. Label and weight features are set to 0.

  Args:
    raw_example: Raw_Example
    vocab_ids: dict<term, id>.

  Returns:
    SequenceExampleWrapper.
  """
  seq = data.SequenceWrapper()
  seq.add_context(raw_example)
  for token in raw_example['sentence']:
    if token in vocab_ids:
      seq.add_timestep().set_token(vocab_ids[token])

  # Add EOS token to end
  seq.add_timestep().set_token(vocab_ids[EOS_TOKEN])

  return seq


def _generate_training_data(vocab_ids, writer_lm_all, writer_seq_ae_all):
  """Generates training data."""

  # Construct training data writers
  writer_lm = _shuff_writer(TRAIN_LM)
  writer_seq_ae = _shuff_writer(TRAIN_SA)
  writer_class = _shuff_writer(TRAIN_CLASS)
  writer_rev_lm = _shuff_writer(TRAIN_REV_LM)
  writer_bd_class = _shuff_writer(TRAIN_BD_CLASS)
  writer_bd_valid_class = _shuff_writer(VALID_BD_CLASS)

  for example in data.raw_dataset(FLAGS.train_file):
    input_seq = _build_input_sequence(example, vocab_ids)

  # TODO

  

  for doc in document_generators.documents(
      dataset='train', include_unlabeled=True, include_validation=True):
    input_seq = build_input_sequence(doc, vocab_ids)
    if len(input_seq) < 2:
      continue
    rev_seq = data.build_reverse_sequence(input_seq)
    lm_seq = data.build_lm_sequence(input_seq)
    rev_lm_seq = data.build_lm_sequence(rev_seq)
    seq_ae_seq = data.build_seq_ae_sequence(input_seq)
    if doc.label is not None:
      # Used for sentiment classification.
      label_seq = data.build_labeled_sequence(
          input_seq,
          doc.label,
          label_gain=(FLAGS.label_gain and not doc.is_validation))
      bd_label_seq = data.build_labeled_sequence(
          data.build_bidirectional_seq(input_seq, rev_seq),
          doc.label,
          label_gain=(FLAGS.label_gain and not doc.is_validation))
      class_writer = writer_valid_class if doc.is_validation else writer_class
      bd_class_writer = (writer_bd_valid_class
                         if doc.is_validation else writer_bd_class)
      class_writer.write(label_seq.seq.SerializeToString())
      bd_class_writer.write(bd_label_seq.seq.SerializeToString())

    # Write
    lm_seq_ser = lm_seq.seq.SerializeToString()
    seq_ae_seq_ser = seq_ae_seq.seq.SerializeToString()
    writer_lm_all.write(lm_seq_ser)
    writer_seq_ae_all.write(seq_ae_seq_ser)
    if not doc.is_validation:
      writer_lm.write(lm_seq_ser)
      writer_rev_lm.write(rev_lm_seq.seq.SerializeToString())
      writer_seq_ae.write(seq_ae_seq_ser)

  # Close writers
  writer_lm.close()
  writer_seq_ae.close()
  writer_class.close()
  writer_valid_class.close()
  writer_rev_lm.close()
  writer_bd_class.close()
  writer_bd_valid_class.close()


def _generate_test_data(vocab_ids, writer_lm_all, writer_seq_ae_all):
  """Generates test data."""
  for example in data.raw_dataset(FLAGS.test_file):
    input_seq = _build_input_sequence(example, vocab_ids)


  # Construct test data writers
  writer_lm = build_shuffling_tf_record_writer(data.TEST_LM)
  writer_rev_lm = build_shuffling_tf_record_writer(data.TEST_REV_LM)
  writer_seq_ae = build_shuffling_tf_record_writer(data.TEST_SA)
  writer_class = build_tf_record_writer(data.TEST_CLASS)
  writer_bd_class = build_shuffling_tf_record_writer(data.TEST_BD_CLASS)

  for doc in document_generators.documents(
      dataset='test', include_unlabeled=False, include_validation=True):
    input_seq = build_input_sequence(doc, vocab_ids)
    if len(input_seq) < 2:
      continue
    rev_seq = data.build_reverse_sequence(input_seq)
    lm_seq = data.build_lm_sequence(input_seq)
    rev_lm_seq = data.build_lm_sequence(rev_seq)
    seq_ae_seq = data.build_seq_ae_sequence(input_seq)
    label_seq = data.build_labeled_sequence(input_seq, doc.label)
    bd_label_seq = data.build_labeled_sequence(
        data.build_bidirectional_seq(input_seq, rev_seq), doc.label)

    # Write
    writer_class.write(label_seq.seq.SerializeToString())
    writer_bd_class.write(bd_label_seq.seq.SerializeToString())
    lm_seq_ser = lm_seq.seq.SerializeToString()
    seq_ae_seq_ser = seq_ae_seq.seq.SerializeToString()
    writer_lm.write(lm_seq_ser)
    writer_rev_lm.write(rev_lm_seq.seq.SerializeToString())
    writer_seq_ae.write(seq_ae_seq_ser)
    writer_lm_all.write(lm_seq_ser)
    writer_seq_ae_all.write(seq_ae_seq_ser)

  # Close test writers
  writer_lm.close()
  writer_rev_lm.close()
  writer_seq_ae.close()
  writer_class.close()
  writer_bd_class.close()


def gen_data(vocab_ids):
  tf.logging.set_verbosity(tf.logging.INFO)
  # tf.logging.info('Assigning vocabulary ids...')

  with _shuff_writer(ALL_LM) as writer_lm_all:
    with _shuff_writer(ALL_SA) as writer_seq_ae_all:
      tf.logging.info('Generating training data...')
      _generate_training_data(vocab_ids, writer_lm_all, writer_seq_ae_all)

      tf.logging.info('Generating test data...')
      _generate_test_data(vocab_ids, writer_lm_all, writer_seq_ae_all)
