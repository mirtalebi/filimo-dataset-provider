from huggingface_hub import hf_hub_download
hf_hub_download(repo_id="farsi-asr/filimo-chunked-asr-dataset", filename="data.db", repo_type="dataset", local_dir="content")

