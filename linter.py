import json
# import os
# import sys
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

    def find_errors(self, output):
        '''function to find errors'''
        # if os.path.exists(os.path.join(self.working_dir, 'Cargo.toml')):
        #     sys.exit()

        lint_match = SLlint.LintMatch

        for i in output.splitlines():
            try:
                compiled = json.loads(i)
            except:
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
            for spansobj in spans:
                msg = mainmessage
                if spansobj['label'] is not None:
                    if spansobj['label'] != '':
                        msg += '\n' + spansobj['label']
                if spansobj['suggested_replacement'] is not None:
                    if spansobj['suggested_replacement'] != '':
                        msg += '\n' + spansobj['suggested_replacement']
                if spansobj['suggestion_applicability'] is not None:
                    if spansobj['suggestion_applicability'] != '':
                        msg += ' ('+spansobj['suggestion_applicability']+')'
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
                for span in spansobj['expansion']['span']:
                    msg = mainmessage
                    if span['label'] is not None:
                        if span['label'] != '':
                            msg += '\n' + span['label']
                    if span['suggested_replacement'] is not None:
                        if span['suggested_replacement'] != '':
                            msg += '\n' + span['suggested_replacement']
                    if span['suggestion_applicability'] is not None:
                        if span['suggestion_applicability'] != '':
                            msg += ' ('+span['suggestion_applicability']+')'
                    yield lint_match(
                        filename=span['file_name'],
                        line=span['line_start']-1,
                        end_line=span['line_end']-1,
                        col=span['column_start']-1,
                        end_col=span['column_end']-1,
                        error_type=level,
                        code=code,
                        message=msg
                    )

            for child in compiled['children']:
                if child['spans']:
                    mainmessage = child['message']
                    level = child['level']
                    if child['code'] is None:
                        code = ''
                    else:
                        code = child['code']['code']
                    level = child['warning']
                    spans = child['spans']
                    for spans in child['spans']:
                        msg = mainmessage
                        if spans['label'] is not None:
                            if spans['label'] != '':
                                msg += '\n' + spans['label']
                        if spans['suggested_replacement'] is not None:
                            if spans['suggested_replacement'] != '':
                                msg += '\n' + spans['suggested_replacement']
                        if spans['suggestion_applicability'] is not None:
                            if spans['suggestion_applicability'] != '':
                                msg += ' (' \
                                    + spans['suggestion_applicability'] + ')'
                        yield lint_match(
                            filename=spans['file_name'],
                            line=spans['line_start']-1,
                            end_line=spans['line_end']-1,
                            col=spans['column_start']-1,
                            end_col=spans['column_end']-1,
                            error_type=level,
                            code=code,
                            message=msg
                        )
