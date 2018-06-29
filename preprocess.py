#-*- coding: UTF-8 -*-
#!/usr/bin/python3
"""
@Author Yi Zhu
Upated  06/29/2018  
preprocessing scripts
"""

#************************************************************
# Imported Libraries
#************************************************************
import argparse
import os

import pdb

def create_args():
  parser = argparse.ArgumentParser(description = 'Preprocessing Scripts')
  parser.add_argument('--input_dir', type = str, required = True,
      help ='input directory')
  parser.add_argument('--output', type = str, default = 'out',
      help ='output')
  args = parser.parse_args()
  return args


def proc(args):
  data = []
  for root, dirs, files in os.walk(args.input_dir):
    for f in files:
      base_dir = os.path.basename(root)
      if base_dir not in f:
        continue
      if 'train' not in f:
        continue
      file_name = os.path.join(root, f)
      get_file_data(file_name, data)


def get_file_data(file_name, data):
  with open(file_name, 'r') as f:
    lines = f.readlines()
  i = 0
  # prune
  for line in lines:
    line = line.strip()
    # empty string
    if not line:
      continue
    # comments
    if line.startswith('#'):
      continue
    linevec = line.split('\t')
    # delete punctuation, numbers
    if linevec[3] == 'PUNCT' or linevec[3] == 'NUM':
      continue
    stem = normalize(linevec[2])
    word = normalize(linevec[1])
    tags = prune_tag(linevec) 

    if not tags or word == stem:
      continue
    tags = ' '.join(tags)

    inst = [stem, tags, word]
    inst = [l for l in inst if l]
    data.append((' '.join(inst), linevec[5], linevec[3]))
    i += 1
    if i == 10000:
      break

  with open('./data/fitrain', 'r') as fin:
    gold_data = fin.read().strip().split('\n')
  for i, gl in enumerate(gold_data):
    if gl != data[i][0]:
      print(i)
      print(gl)
      print(data[i])
      if 'derivation' in data[i][0]:
        continue
      break


def normalize(token):
  token = token.lower()
  token = token.replace('#', '')
  return token


def prune_tag(linevec):
  v_tags = []
  tags = normalize_tags(linevec)
  for k in tags:
    for v in tags[k]:
      tag = valid_tag(k, v, linevec)
    if tag is not None:
      v_tags.append(tag)
  return v_tags


def normalize_tags(linevec):
  norm_tags = {}
  tags = linevec[5].strip().lower().split('|')
  # empty morphological tags
  if tags == ['_']:
    return {}
  for tag in tags:
    tagvec = tag.strip().split('=')
    k = tagvec[0]
    vs = tagvec[1].split(',')
    if k not in norm_tags:
      norm_tags[k] = vs
    else:
      norm_tags[k].extend(vs)
  return norm_tags


def valid_tag(k, v, linevec):
  sub_tags = {
      'VERB'    : {'number': {'sing': 'singv',
                              'plur': 'plurv'}, 
                   'person': {'0': '3'},},
      'AUX'     : {'number': {'sing': 'singv',
                             'plur': 'plurv'},
                   'person': {'0': '3'},},
      }
  pos = linevec[3] 
  # substitute pos tag specific morphological tag
  if pos in sub_tags and k in sub_tags[pos] and v in sub_tags[pos][k]:
    tag = k + '=' + sub_tags[pos][k][v]
    return tag

  inv_tags = {
      'style'         : ['arch', 'coll'],
      'abbr'          : ['yes'],
      'numtype'       : ['ord'],
      'degree'        : ['pos'],
      'case'          : ['nom'],
      'number'        : ['sing'],
      'number[psor]'  : ['plur', 'sing'],
      'prontype'      : ['prs', 'dem', 'ind', 'rcp', 'int', 'rel'],
      'mood'          : ['ind'], 
      'tense'         : ['pres'],
      'verbform'      : ['fin', 'part'], 
      'voice'         : ['act'],
      'polarity'      : ['neg'],
      'infform'       : ['1', '2', '3'],
      'adptype'       : ['post', 'prep'],
      'typo'          : ['yes'],
      'reflex'        : ['yes'],
      'foreign'       : ['yes'],
      'connegative'   : ['yes'],
      }
  if k in inv_tags and v in inv_tags[k]:
    return None
  tag = k + '=' + v
  return tag


if __name__ == '__main__':
  args = create_args()
  proc(args)
