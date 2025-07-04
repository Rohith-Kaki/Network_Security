import os

class s3sync:
    def sync_folder_to_s3(self, folder, aws_bucket_url):
        commnad = f'aws s3 sync {folder} {aws_bucket_url}'
        os.system(commnad)

    def sync_s3_to_folder(self, folder, aws_bucket_url):
        commnad = f'aws s3 sync {aws_bucket_url} {folder}'
        os.system(commnad)