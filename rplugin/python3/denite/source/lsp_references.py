import logging
import os
from urllib.parse import urlparse

from .base import Base

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.FileHandler('denitevimlsp.log')
fmt = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
handler.setFormatter(fmt)
handler.setLevel(logging.INFO)
logger.addHandler(handler)


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'lsp_references'
        self.kind = 'file'

        self.vim.vars['denite#source#vim_lsp#_results'] = []
        self.vim.vars['denite#source#vim_lsp#_request_completed'] = False

    def gather_candidates(self, context):
        if context['is_async']:
            if self.vim.vars['denite#source#vim_lsp#_request_completed']:
                context['is_async'] = False
                return make_candidates(
                    self.vim.vars['denite#source#vim_lsp#_results'])
            return []

        self.vim.vars['denite#source#vim_lsp#_request_completed'] = False
        context['is_async'] = True
        self.vim.call('denite_vim_lsp#references')
        return []


def make_candidates(locations):
    if not locations:
        logger.info('location nothing')
        return []
    if not isinstance(locations, list):
        logger.info('location is not list')
        return []
    candidates = [_parse_candidate(loc) for loc in locations]
    return candidates


def _parse_candidate(loc):
    candidate = {}
    candidate['word'] = "{}:{}: {}".format(os.path.relpath(loc['filename']), loc['lnum'], loc['text'])
    candidate['action__path'] = os.path.abspath(loc['filename'])
    candidate['action__line'] = loc['lnum']+1
    candidate['action__col'] = loc['col']+1
    return candidate
