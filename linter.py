import json
import os
import sys
import SublimeLinter.lint as SLlint    # Linter, LintMatch, STREAM_STDERR


class Rustc(SLlint.Linter):
    '''rustc linter'''

    cmd = (
        'rustc', '--error-format=json', '--emit=mir', '-o', '/dev/null',
        '${file}'
    )
    defaults = {
        'selector': 'source.rust'
    }
    error_stream = SLlint.STREAM_STDERR
    name = 'rust'
    on_stderr = None
    tempfile_suffix = '-'

    def init(self):
        '''placeholder'''
        print(self)

    def find_errors(self, output):
        '''function to find errors'''

        def pathtest(badpath):
            pathvec_init = badpath.replace('\\', '/').split('/')
            pathvec_init.pop()
            path = '/'.join(pathvec_init) + '/Cargo.toml'
            for _ in range(0, 10):
                if os.path.exists(path):
                    sys.exit()
                else:
                    pathvec = path.split('/')
                    if len(pathvec) >= 3:
                        pathvec.pop(-2)
                        path = '/'.join(pathvec)
                    else:
                        break

        path = self.context.get('file')
        pathtest(path)

        def for_loop(spans_list, mainmessage, level, code, lint_match):
            '''yield lints'''

            def labelcheck(message, spansobj):
                '''addons to msg'''
                msg = message
                if spansobj['label'] is not None:
                    if spansobj['label'] != '':
                        msg += '\n' + spansobj['label']
                if spansobj['suggested_replacement'] is not None:
                    if spansobj['suggested_replacement'] != '':
                        msg += '\n' + spansobj['suggested_replacement']
                if spansobj['suggestion_applicability'] is not None:
                    if spansobj['suggestion_applicability'] != '':
                        msg += ' ('+spansobj['suggestion_applicability']+')'
                return msg

            for spansobj in spans_list:
                msg = labelcheck(mainmessage, spansobj)
                yield lint_match(
                    filename=spansobj['file_name'],
                    line=spansobj['line_start']-1,
                    end_line=spansobj['line_end']-1,
                    col=spansobj['column_start']-1,
                    end_col=spansobj['column_end']-1,
                    error_type=level,
                    code=code,
                    message=msg
                )
                if spansobj['is_primary'] is True:
                    for child in compiled['children']:
                        if not child['spans']:
                            if child['code'] is None:
                                code = ''
                            else:
                                code = child['code']
                            yield lint_match(
                                filename=spansobj['file_name'],
                                line=spansobj['line_start']-1,
                                end_line=spansobj['line_end']-1,
                                col=spansobj['column_start']-1,
                                end_col=spansobj['column_end']-1,
                                error_type=child['level'],
                                code=code,
                                message=child['message']
                            )
                if spansobj['expansion'] is None:
                    continue
                yield from for_loop(
                    spansobj['expansion']['span'],
                    mainmessage, level, code, lint_match
                )

        lint_match = SLlint.LintMatch

        for i in output.splitlines():
            try:
                compiled = json.loads(i)
            except ValueError:
                continue

            mainmessage = compiled['message']

            if compiled['code'] is None:
                code = ''
            else:
                code = compiled['code']['code']

            level = compiled['level']

            spans = compiled['spans']
            if spans is None:
                yield lint_match(
                    filename=self.get.context('file'),
                    line=0,
                    end_line=1,
                    col=0,
                    end_col=1,
                    error_type=level,
                    code=code,
                    message=mainmessage
                )

            yield from for_loop(spans, mainmessage, level, code, lint_match)

            for child in compiled['children']:
                if child['spans']:
                    mainmessage = child['message']
                    level = child['level']
                    if child['code'] is None:
                        code = ''
                    else:
                        code = child['code']['code']
                    level = child['level']
                    spans = child['spans']
                    yield from for_loop(
                        spans, mainmessage, level, code, lint_match
                    )
