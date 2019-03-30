# depccg v1
Codebase for [A\* CCG Parsing with a Supertag and Dependency Factored Model](https://arxiv.org/abs/1704.06936)

### Requirements

* Python >= 3.6.0
* A C++ compiler supporting [C++11 standard](https://en.wikipedia.org/wiki/C%2B%2B11) (in case of gcc, must be >= 4.8)
* OpenMP (optional, for efficient batched parsing)


## Installation

Using pip:
```sh
➜ pip install git+https://github.com/masashi-y/depccg.git@refactor
```

If OpenMP is available in your environment, you can use it for more efficient parsing:
```sh
➜ USE_OPENMP=1 pip install git+https://github.com/masashi-y/depccg.git@refactor
```

## Usage

### Using a pretrained English parser

__Better performing ELMo model is also [available](#the-best-performing-elmo-model) now.__

The best performing model in the paper trained on tri-training is available:
```sh
➜ depccg_en download
```

It can be downloaded directly [here](http://cl.naist.jp/~masashi-y/resources/depccg/en_hf_tri.tar.gz) (189M).


```sh
➜ echo "this is a test sentence ." | depccg_en
ID=1, Prob=-0.0006299018859863281
(<T S[dcl] 0 2> (<T S[dcl] 0 2> (<L NP XX XX this NP>) (<T S[dcl]\NP 0 2> (<L (S[dcl]\NP)/NP XX XX is (S[dcl]\NP)/NP>) (<T NP 0 2> (<L NP[nb]/N XX XX a NP[nb]/N>) (<T N 0 2> (<L N/N XX XX test N/N>) (<L N XX XX sentence N>) ) ) ) ) (<L . XX XX . .>) )
```
You can specify output format (see [below](#available-output-formats)).

```sh
➜ echo "this is a test sentence ." | depccg_en --format deriv
ID=1, Prob=-0.0006299018859863281
 this        is           a      test  sentence  .
  NP   (S[dcl]\NP)/NP  NP[nb]/N  N/N      N      .
                                ---------------->
                                       N
                      -------------------------->
                                  NP
      ------------------------------------------>
                      S[dcl]\NP
------------------------------------------------<
                     S[dcl]
---------------------------------------------------<rp>
                      S[dcl]
```

By default, the input is expected to be pre-tokenized. If you want to process untokenized sentences, you can pass `--tokenize` option.

The POS and NER tags in the output are filled with `XX` by default. You can replace them with ones predicted using [SpaCy](https://spacy.io):
```sh
➜ pip install spacy
➜ python -m spacy download en
➜ echo "this is a test sentence ." | depccg_en --annotator spacy
ID=1, Prob=-0.0006299018859863281
(<T S[dcl] 0 2> (<T S[dcl] 0 2> (<L NP DT DT this NP>) (<T S[dcl]\NP 0 2> (<L (S[dcl]\NP)/NP VBZ VBZ is (S[dcl]\NP)/NP>) (<T NP 0 2> (<L NP[nb]/N DT DT a NP[nb]/N>) (<T N 0 2> (<L N/N NN NN test N/N>) (<L N NN NN sentence N>) ) ) ) ) (<L . . . . .>) )
```
The parser uses a SpaCy's model symbolic-linked to `en` (it loads a model by `spacy('en')`).

Orelse, you can use POS/NER taggers implemented in [C&C](https://www.cl.cam.ac.uk/~sc609/candc-1.00.html), which may be useful in some sorts of parsing experiments:

```sh
➜ export CANDC=/path/to/candc
➜ echo "this is a test sentence ." | depccg_en --annotator candc
ID=1, Prob=-0.0006299018859863281
(<T S[dcl] 0 2> (<T S[dcl] 0 2> (<L NP DT DT this NP>) (<T S[dcl]\NP 0 2> (<L (S[dcl]\NP)/NP VBZ VBZ is (S[dcl]\NP)/NP>) (<T NP 0 2> (<L NP[nb]/N DT DT a NP[nb]/N>) (<T N 0 2> (<L N/N NN NN test N/N>) (<L N NN NN sentence N>) ) ) ) ) (<L . . . . .>) )
```

By default, depccg expects the POS and NER models are placed in `$CANDC/models/pos` and `$CANDC/models/ner`, but you can explicitly specify them by setting `CANDC_MODEL_POS` and `CANDC_MODEL_NER` environmental variables.

It is also possible to obtain logical formulas using [ccg2lambda](https://github.com/mynlp/ccg2lambda)'s semantic parsing algorithm.
```sh
➜ echo "This is a test sentence ." | depccg_en --format ccg2lambda --annotator spacy
ID=0 log probability=-0.0006299018859863281
exists x.(_this(x) & True & exists z1.(_sentence(z1) & _test(z1) & True & (x = z1)))
```

### The best performing ELMo model


In accordance with many other reported results, depccg obtains the improved performance by using contextualized word embeddings ([ELMo](https://allennlp.org/elmo); Peters et al., 2018).

The ELMo model replaces affix embeddings in (Yoshikawa et al., 2017) with ELMo, resulting in 1124 dimensional input embeddings (ELMo + GloVe). It is trained on CCGbank and the [tri-training](#training-model) silver dataset.

||Unlabeled F1|Labeled F1|
|:-|:-|:-|
|(Yoshikawa et al., 2017)|94.0|88.8|
|+ELMo|94.98|90.51|


Please download the model from the following link.
* [English ELMo model](https://cl.naist.jp/~masashi-y/resources/depccg/lstm_parser_elmo_finetune.tar.gz) (649M)

To use the model, install `allennlp`:

```sh
➜ pip install allennlp
```

and then,
```sh
➜ tar xvf lstm_parser_elmo_finetune.tar.gz
➜ echo "this is a test sentence ." | depccg_en --model lstm_parser_elmo_finetune
```

Using a GPU (by `--gpu` option) is recommended if possible.

### Using a pretrained Japanese parser

The best performing model is available by:
```sh
➜ depccg_ja download
```

It can be downloaded directly [here](http://cl.naist.jp/~masashi-y/resources/depccg/ja_hf_ccgbank.tar.gz) (56M).

The Japanese parser depends on [Janome](https://github.com/mocobeta/janome) for the tokenization. Please install it by:
```sh
➜ pip install janome
```

The parser provides the almost same interface as with the English one, with slight differences including the default output format, which is now one compatible with the Japanese CCGbank:
```sh
➜ echo "これはテストの文です。" | depccg_ja
ID=1, Prob=-53.98793411254883
{< S[mod=nm,form=base,fin=t] {< S[mod=nm,form=base,fin=f] {< NP[case=nc,mod=nm,fin=f] {NP[case=nc,mod=nm,fin=f] これ/これ/**} {NP[case=nc,mod=nm,fin=f]\NP[case=nc,mod=nm,fin=f] は/は/**}} {< S[mod=nm,form=base,fin=f]\NP[case=nc,mod=nm,fin=f] {< NP[case=nc,mod=nm,fin=f] {< NP[case=nc,mod=nm,fin=f] {NP[case=nc,mod=nm,fin=f] テスト/テスト/**} {NP[case=nc,mod=nm,fin=f]\NP[case=nc,mod=nm,fin=f] の/の/**}} {NP[case=nc,mod=nm,fin=f]\NP[case=nc,mod=nm,fin=f] 文/文/**}} {(S[mod=nm,form=base,fin=f]\NP[case=nc,mod=nm,fin=f])\NP[case=nc,mod=nm,fin=f] です/です/**}}} {S[mod=nm,form=base,fin=t]\S[mod=nm,form=base,fin=f] 。/。/**}}
```

You can pass pre-tokenized sentences as well:
```sh
➜ echo "これ は テスト の 文 です 。" | depccg_ja --pre-tokenized
ID=1, Prob=-53.98793411254883
{< S[mod=nm,form=base,fin=t] {< S[mod=nm,form=base,fin=f] {< NP[case=nc,mod=nm,fin=f] {NP[case=nc,mod=nm,fin=f] これ/これ/**} {NP[case=nc,mod=nm,fin=f]\NP[case=nc,mod=nm,fin=f] は/は/**}} {< S[mod=nm,form=base,fin=f]\NP[case=nc,mod=nm,fin=f] {< NP[case=nc,mod=nm,fin=f] {< NP[case=nc,mod=nm,fin=f] {NP[case=nc,mod=nm,fin=f] テスト/テスト/**} {NP[case=nc,mod=nm,fin=f]\NP[case=nc,mod=nm,fin=f] の/の/**}} {NP[case=nc,mod=nm,fin=f]\NP[case=nc,mod=nm,fin=f] 文/文/**}} {(S[mod=nm,form=base,fin=f]\NP[case=nc,mod=nm,fin=f])\NP[case=nc,mod=nm,fin=f] です/です/**}}} {S[mod=nm,form=base,fin=t]\S[mod=nm,form=base,fin=f] 。/。/**}}
```

### Available output formats

* `auto` - the most standard format following AUTO format in the English CCGbank
* `deriv` - visualized derivations in ASCII art
* `xml` - XML format compatible with C&C's XML format (only for English parsing)
* `conll` - CoNLL format
* `html` - visualized trees in MathML
* `prolog` - Prolog-like format
* `jigg_xml` - XML format compatible with [Jigg](https://github.com/mynlp/jigg)
* `ptb` - Penn Treebank-style format
* `ccg2lambda` - logical formula converted from a derivation using [ccg2lambda](https://github.com/mynlp/ccg2lambda)
* `jigg_xml_ccg2lambda` - jigg_xml format with ccg2lambda logical formula inserted
* `json` - JSON format
* `ja` - a format adopted in Japanese CCGbank (only for Japanese)

### Programatic Usage

```python
from depccg.parser import EnglishCCGParser
from pathlib import Path

# Available keyword arguments in initializing a CCG parser
# Please refer to the following paper for category dictionary, seen rules, pruning etc.
# "A* CCG Parsing with a Supertag-factored Model", Lewis and Steedman, 2014
kwargs = dict(
    # A list of binary rules 
    # By default: depccg.combinator.en_default_binary_rules
    binary_rules=None,
    # Penalize an application of a unary rule by adding this value (negative log probability)
    unary_penalty=0.1,
    # Prune supertags with low probabilities using this value
    beta=0.00001,
    # Set False if not prune
    use_beta=True,
    # Use category dictionary
    use_category_dict=True,
    # Use seen rules
    use_seen_rules=True,
    # This also used to prune supertags
    pruning_size=50,
    # Nbest outputs
    nbest=1,
    # Limit categories that can appear at the root of a CCG tree
    # By default: S[dcl], S[wq], S[q], S[qem], NP.
    possible_root_cats=None,
    # Give up parsing long sentences
    max_length=250,
    # Give up parsing if it runs too many steps
    max_steps=100000,
    # You can specify a GPU
    gpu=-1
)

# Initialize a parser from a model directory
model = "/path/to/model/directory"
parser = EnglishCCGParser.from_dir(
    model,
    load_tagger=True, # Load supertagging model
    **kwargs)

model = Path("/path/to/model/directory")
parser = EnglishCCGParser.from_files(
    unary_rules=model / 'unary_rules.txt',
    category_dict=model / 'cat_dict.txt',
    seen_rules=model / 'seen_rules.txt',
    tagger_model_dir=model / 'tagger_model',
    **kwargs)

# If you don't like to keep separate files,
# wget http://cl.naist.jp/~masashi-y/resources/depccg/config.json
model = Path("/path/to/model/directory")
parser = EnglishCCGParser.from_json(
    model / 'config.json',
    tagger_model_dir=model / 'tagger_model',
    **kwargs)

sents = [
  "This is a test sentence .",
  "This is second ."
]

results = praser.parse_doc(sents)
for nbests in results:
    for tree, log_prob in nbests:
        print(tree.deriv)
```

For Japanese CCG parsing, use `depccg.JapaneseCCGParser`,
which has the exactly same interface.
Note that the Japanese parser accepts pre-tokenized sentences as input.

## Train your own model

You can use my [allennlp](https://allennlp.org/)-based supertagger and extend it.

To train a supertagger, compress the English ccgbank into a json file by command:
```sh
➜ python -m depccg.tools.data --mode train /path/to/ccgbank/wsj_02-21.auto out_directory
➜ python -m depccg.tools.data --mode test /path/to/ccgbank/wsj_00.auto out_directory
```
which will outputs `traindata.json` and `testdata.json`. Then download [vocab](http://cl.naist.jp/~masashi-y/resources/depccg/vocabulary.tar.gz):
```sh
➜ wget http://cl.naist.jp/~masashi-y/resources/depccg/vocabulary.tar.gz
➜ tar xvf vocabulary.tar.gz
```

Then finally,
```sh
➜ vocab=vocabulary train_data=traindata.json test_data=testdata.json gpu=0 \
  encoder_type=lstm token_embedding_type=char \
  allennlp train --include-package depccg.models.my_allennlp --serialization-dir results supertagger.jsonnet
```
The training configs are passed either through environmental variables or directly writing to jsonnet config files, which are available in [supertagger.jsonnet](depccg/models/my_allennlp/config/supertagger.jsonnet) or [supertagger_tritrain.jsonnet](depccg/models/my_allennlp/config/supertagger_tritrain.jsonnet).
The latter is a config file for using [tri-training silver data](http://cl.naist.jp/~masashi-y/resources/depccg/headfirst_parsed.conll.stagged.gz) (309M) constructed in (Yoshikawa et al., 2017), on top of the English CCGbank.

To use the trained supertagger,
```sh
➜ echo '{"sentence": "this is a test sentence ."}' > input.jsonl
➜ allennlp predict results/model.tar.gz --include-package depccg.models.my_allennlp --output-file weights.json input.jsonl
➜ cat weights.json | depccg_en --input-format json
```
where `weights.json` contains probabilities used in the parser (`p_tag` and `p_dep`).

Alternatively, you can download the [pretrained ELMo model](#the-best-performing-elmo-model) and replace `tagger_model.tar.gz` contained in it with the `results/model.tar.gz`.

## Miscellaneous

### Diff tool

In error analysis, you must want to see diffs between trees in an intuitive way.
`depccg.tools.diff` does exactly this:

```sh
➜ python -m depccg.tools.diff file1.auto file2.auto > diff.html
```

which outputs:

![show diffs between trees](images/diff.png)

where trees in the same lines of the files are compared and the diffs are marked in color.

## Citation

If you make use of this software, please cite the following:

    @inproceedings{yoshikawa:2017acl,
      author={Yoshikawa, Masashi and Noji, Hiroshi and Matsumoto, Yuji},
      title={A* CCG Parsing with a Supertag and Dependency Factored Model},
      booktitle={Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)},
      publisher={Association for Computational Linguistics},
      year={2017},
      pages={277--287},
      location={Vancouver, Canada},
      doi={10.18653/v1/P17-1026},
      url={http://aclweb.org/anthology/P17-1026}
    }



## Licence
MIT Licence

## Contact
For questions and usage issues, please contact yoshikawa.masashi.yh8@is.naist.jp .

## Acknowledgement
In creating the parser, I owe very much to:
- [EasyCCG](https://github.com/mikelewis0/easyccg): from which I learned everything
- [NLTK](http://www.nltk.org/): for nice pretty printing for parse derivation
