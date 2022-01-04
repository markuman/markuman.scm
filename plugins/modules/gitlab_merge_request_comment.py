#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: gitlab_merge_request_comment
short_description: write messages to gitlab merge requests
description:
  - write messages to gitlab merge requests.
  - works only if `CI_OPEN_MERGE_REQUESTS` is defined
  - it's designed to run inside gitlab ci/cd pipeline
version_added: "1.0.0"
author:
  - "Markus Bergholz (@markuman)"
options:
  comment:
    description:
      - Comment message.
    required: true
    type: str
  api_url:
    description:
      - Your gitlab url
    required: true
  api_token:
    description:
      - API Token.
      - If not provided, it's read from ENV ANSIBLE_GITLAB_API_TOKEN
    required: false
    type: str
'''

EXAMPLES = '''
    - name: post message
      markuman.scm.gitlab_merge_request_comment:
        api_url: gitlab.com
        comment: |
          Summary

          | some | table |
          | --- | --- |
          | yes | 🐧 |
'''

from ansible.module_utils.basic import AnsibleModule
import requests
import os


def main():
    module = AnsibleModule(
        argument_spec=dict(
            comment=dict(required=True, type='str'),
            api_token=dict(required=False, type='str', no_log=True),
            api_url=dict(required=True, type='str')
        )
    )

    comment = module.params.get("comment")
    api_url = module.params.get("api_url")
    api_token = module.params.get("api_token") or os.environ.get('ANSIBLE_GITLAB_API_TOKEN')

    _mr_id = os.environ.get('CI_OPEN_MERGE_REQUESTS')

    if _mr_id and api_token:
        mr_id = _mr_id.split('!')[-1]
        pr_id = os.environ.get('CI_PROJECT_ID')
        gitlab_mr_url = f'https://{api_url}/api/v4/projects/{pr_id}/merge_requests/{mr_id}/notes'

        headers = {
            'Accept': 'application/json',
            'Private-Token': api_token
        }

        data = {
            'body': comment
        }

        x = requests.post(gitlab_mr_url, data = data, headers = headers)

        change = False
        if x.status_code == 201:
            change = True

        module.exit_json(changed=change, status=x.status_code)

    else:
        module.exit_json(changed=False, status=None)


if __name__ == '__main__':
    main()
