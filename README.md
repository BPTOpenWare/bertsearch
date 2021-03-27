# Elasticsearch meets BERT AND SCRAPYD!

This is a simple combination of several open source projects under an MIT license. The majority has been pulled from the forked github project. Modifications and spiders included are also under a MIT license. 

Below is a job search example:

![An example of bertsearch](./docs/example.png)

## System architecture

![System architecture](./docs/architecture.png)

## Requirements

- Docker
- Docker Compose >= [1.22.0](https://docs.docker.com/compose/release-notes/#1220)

## Getting Started

### 1. Download a pretrained BERT model

The model is currenlt configured for uncased 1024 per the .env file.

<details>
 <summary>List of released pretrained BERT models (click to expand...)</summary>


<table>
<tr><td><a href="https://storage.googleapis.com/bert_models/2018_10_18/uncased_L-12_H-768_A-12.zip">BERT-Base, Uncased</a></td><td>12-layer, 768-hidden, 12-heads, 110M parameters</td></tr>
<tr><td><a href="https://storage.googleapis.com/bert_models/2018_10_18/uncased_L-24_H-1024_A-16.zip">BERT-Large, Uncased</a></td><td>24-layer, 1024-hidden, 16-heads, 340M parameters</td></tr>
<tr><td><a href="https://storage.googleapis.com/bert_models/2018_10_18/cased_L-12_H-768_A-12.zip">BERT-Base, Cased</a></td><td>12-layer, 768-hidden, 12-heads , 110M parameters</td></tr>
<tr><td><a href="https://storage.googleapis.com/bert_models/2018_10_18/cased_L-24_H-1024_A-16.zip">BERT-Large, Cased</a></td><td>24-layer, 1024-hidden, 16-heads, 340M parameters</td></tr>
<tr><td><a href="https://storage.googleapis.com/bert_models/2018_11_23/multi_cased_L-12_H-768_A-12.zip">BERT-Base, Multilingual Cased (New)</a></td><td>104 languages, 12-layer, 768-hidden, 12-heads, 110M parameters</td></tr>
<tr><td><a href="https://storage.googleapis.com/bert_models/2018_11_03/multilingual_L-12_H-768_A-12.zip">BERT-Base, Multilingual Cased (Old)</a></td><td>102 languages, 12-layer, 768-hidden, 12-heads, 110M parameters</td></tr>
<tr><td><a href="https://storage.googleapis.com/bert_models/2018_11_03/chinese_L-12_H-768_A-12.zip">BERT-Base, Chinese</a></td><td>Chinese Simplified and Traditional, 12-layer, 768-hidden, 12-heads, 110M parameters</td></tr>
</table>

</details>

```bash
$ wget https://storage.googleapis.com/bert_models/2018_10_18/uncased_L-24_H-1024_A-16.zip
$ unzip cased_L-12_H-768_A-12.zip
```

### 2. Set environment variables

You need to set a pretrained BERT model and Elasticsearch's index name as environment variables in the .env file if you chose a different BERT model

Update .env file USER_AGENT and BOT_NAME

Update .env file DEFUSR to a default userid password and BERTADM for the admin password


### 3. Run Docker containers


```bash
$ docker-compose up
```

**CAUTION**: If possible, assign high memory(more than `8GB`) to Docker's memory configuration because BERT container needs high memory.

### 4. Create index

The simple index and BERT indexes are created by visiting http://localhost/createindex 


**CAUTION**: The `dims` value of `text_vector` must need to match the dims of a pretrained BERT model.

### 5. Deploy the default spiders

```bash
$ docker-compose run --rm scrapy
# scrapyd-client deploy
# scrapyd-client spiders -p githubspd
githubspd:
  arcore
  githubreadme
  readthedocs
  unrealengine

```

### 6. Create documents

Once you created an index, and deployed the spiders, you’re ready to index some documents. The point here is to convert your document into a vector using BERT. The resulting vector is stored in the `text_vector` field. 

```
$ docker-compose run --rm scrapy
# scrapyd-client spiders
# scrapyd-client schedule -p githubspd githubreadme
githubspd / githubreadme => b1a40466856311ebad7a0242c0a8b005
```

After running you should see in your console log that the job has finished:

```
scrapyd_1        | 2021-03-15T07:55:10+0000 [-] Process finished:  project='githubspd' spider='githubreadme' job='b1a40466856311ebad7a0242c0a8b005' pid=16 log='/var/lib/scrapyd/logs/githubspd/githubreadme/b1a40466856311ebad7a0242c0a8b005.log' items='file:///var/lib/scrapyd/items/githubspd/githubreadme/b1a40466856311ebad7a0242c0a8b005.jl'

```

### 7. Open browser

Go to <http://127.0.0.1>.
