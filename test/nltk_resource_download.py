import nltk
nltk.set_proxy('https://pypi.tuna.tsinghua.edu.cn/simple')
nltk.download('punkt_tab', download_dir='/Users/lijun/Software/miniconda3/envs/ragflow/nltk_data')
nltk.download('punkt', download_dir='/Users/lijun/Software/miniconda3/envs/ragflow/nltk_data')
nltk.download('wordnet',download_dir='/Users/lijun/Software/miniconda3/envs/ragflow/nltk_data')


nltk.data.path.append("/Users/lijun/Git/nltk_data/packages")