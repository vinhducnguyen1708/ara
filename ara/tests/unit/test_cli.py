#  Copyright (c) 2017 Red Hat, Inc.
#
#  This file is part of ARA: Ansible Run Analysis.
#
#  ARA is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ARA is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ARA.  If not, see <http://www.gnu.org/licenses/>.

import os
import pytest
import shutil
import six
import tempfile

from distutils.version import LooseVersion
from flask_frozen import MissingURLGeneratorWarning
from glob import glob
from lxml import etree
from oslo_serialization import jsonutils
from subunit._to_disk import to_disk

import ara.shell
import ara.cli.record
import ara.cli.generate
import ara.cli.host
import ara.cli.play
import ara.cli.playbook
import ara.cli.result
import ara.cli.task
import ara.db.models as m

from ara.tests.unit.common import ansible_run
from ara.tests.unit.common import TestAra


class TestCLIRecord(TestAra):
    """ Tests for the ARA CLI record commands """
    def setUp(self):
        super(TestCLIRecord, self).setUp()

    def tearDown(self):
        super(TestCLIRecord, self).tearDown()

    def test_record_list(self):
        ctx = ansible_run(ara_record=True)

        cmd = ara.cli.record.RecordList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['-a'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['record'].id)

    def test_record_list_for_playbook(self):
        ctx = ansible_run(ara_record=True)

        cmd = ara.cli.record.RecordList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '--playbook',
            six.text_type(ctx['playbook'].id)
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['record'].id)

    def test_record_list_for_non_existing_playbook(self):
        ansible_run(ara_record=True)

        cmd = ara.cli.record.RecordList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_record_show_by_id(self):
        ctx = ansible_run(ara_record=True)

        cmd = ara.cli.record.RecordShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx['record'].id)])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['record'].id)

    def test_record_show_by_key(self):
        ctx = ansible_run(ara_record=True)

        cmd = ara.cli.record.RecordShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '-b',
            six.text_type(ctx['record'].playbook.id),
            ctx['record'].key
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['record'].id)

    def test_record_show_for_non_existing_data(self):
        ansible_run(ara_record=True)

        cmd = ara.cli.record.RecordShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIHost(TestAra):
    """ Tests for the ARA CLI host commands """
    def setUp(self):
        super(TestCLIHost, self).setUp()

    def tearDown(self):
        super(TestCLIHost, self).tearDown()

    def test_host_list(self):
        ctx = ansible_run()

        cmd = ara.cli.host.HostList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['-a'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['host'].id)

    def test_host_list_for_playbook(self):
        ctx = ansible_run()

        cmd = ara.cli.host.HostList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '--playbook',
            six.text_type(ctx['playbook'].id)
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['host'].id)

    def test_host_list_for_non_existing_playbook(self):
        ansible_run()

        cmd = ara.cli.host.HostList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_host_show_by_id(self):
        ctx = ansible_run()

        cmd = ara.cli.host.HostShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx['host'].id)])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['host'].id)

    def test_host_show_by_name(self):
        ctx = ansible_run()

        cmd = ara.cli.host.HostShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '-b',
            six.text_type(ctx['host'].playbook.id),
            ctx['host'].name
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['host'].id)

    def test_host_show_for_non_existing_host(self):
        ansible_run()

        cmd = ara.cli.host.HostShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIPlay(TestAra):
    """ Tests for the ARA CLI play commands """
    def setUp(self):
        super(TestCLIPlay, self).setUp()

    def tearDown(self):
        super(TestCLIPlay, self).tearDown()

    def test_play_list_all(self):
        ctx = ansible_run()

        cmd = ara.cli.play.PlayList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--all'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['play'].id)

    def test_play_list_playbook(self):
        ctx = ansible_run()

        cmd = ara.cli.play.PlayList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '--playbook',
            six.text_type(ctx['playbook'].id)
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['play'].id)

    def test_play_list_non_existing_playbook(self):
        ansible_run()

        cmd = ara.cli.play.PlayList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_play_show(self):
        ctx = ansible_run()

        cmd = ara.cli.play.PlayShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx['play'].id)])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['play'].id)

    def test_play_show_non_existing(self):
        ansible_run()

        cmd = ara.cli.play.PlayShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIPlaybook(TestAra):
    """ Tests for the ARA CLI playbook commands """
    def setUp(self):
        super(TestCLIPlaybook, self).setUp()

    def tearDown(self):
        super(TestCLIPlaybook, self).tearDown()

    def test_playbook_list(self):
        ctx = ansible_run()

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['playbook'].id)

    def test_playbook_list_complete(self):
        ctx = ansible_run()

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--complete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['playbook'].id)

    def test_playbook_list_complete_with_no_complete(self):
        ansible_run(completed=False)

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--complete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_playbook_list_incomplete(self):
        ctx = ansible_run(completed=False)

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--incomplete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['playbook'].id)

    def test_playbook_list_incomplete_with_no_incomplete(self):
        ansible_run()

        cmd = ara.cli.playbook.PlaybookList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--incomplete'])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_playbook_show(self):
        ctx = ansible_run()

        cmd = ara.cli.playbook.PlaybookShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx['playbook'].id)])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['playbook'].id)

    def test_playbook_show_non_existing(self):
        ansible_run()

        cmd = ara.cli.playbook.PlaybookShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)

    def test_playbook_delete(self):
        # Run two playbook runs
        ctx = ansible_run(ara_record=True)
        ansible_run(gather_facts=False)

        # Assert that we have two playbooks and that we have valid data for
        # the first playbook
        playbooks = m.Playbook.query.all()
        self.assertTrue(len(playbooks) == 2)

        d = m.Record.query.filter(
            m.Record.playbook_id.in_([ctx['playbook'].id])
        )
        self.assertNotEqual(d.count(), 0)
        f = m.File.query.filter(m.File.playbook_id.in_([ctx['playbook'].id]))
        self.assertNotEqual(f.count(), 0)
        p = m.Play.query.filter(m.Play.playbook_id.in_([ctx['playbook'].id]))
        self.assertNotEqual(p.count(), 0)
        t = m.Task.query.filter(m.Task.playbook_id.in_([ctx['playbook'].id]))
        self.assertNotEqual(t.count(), 0)
        tr = m.Result.query.count()  # compared later
        h = m.Host.query.filter(m.Host.playbook_id.in_([ctx['playbook'].id]))
        self.assertNotEqual(h.count(), 0)

        # Delete the first playbook
        cmd = ara.cli.playbook.PlaybookDelete(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx['playbook'].id)])
        cmd.take_action(args)

        # Assert that we only have one playbook left and that records have been
        # deleted
        playbooks = m.Playbook.query.all()
        self.assertTrue(len(playbooks) == 1)

        d = m.Record.query.filter(
            m.Record.playbook_id.in_([ctx['playbook'].id])
        )
        self.assertEqual(d.count(), 0)
        f = m.File.query.filter(m.File.playbook_id.in_([ctx['playbook'].id]))
        self.assertEqual(f.count(), 0)
        p = m.Play.query.filter(m.Play.playbook_id.in_([ctx['playbook'].id]))
        self.assertEqual(p.count(), 0)
        t = m.Task.query.filter(m.Task.playbook_id.in_([ctx['playbook'].id]))
        self.assertEqual(t.count(), 0)
        new_tr = m.Result.query.count()  # compare before and after
        self.assertNotEqual(tr, new_tr)
        h = m.Host.query.filter(m.Host.playbook_id.in_([ctx['playbook'].id]))
        self.assertEqual(h.count(), 0)


class TestCLIResult(TestAra):
    """ Tests for the ARA CLI result commands """
    def setUp(self):
        super(TestCLIResult, self).setUp()

    def tearDown(self):
        super(TestCLIResult, self).tearDown()

    def test_result_list_all(self):
        ctx = ansible_run()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--all'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['result'].id)

    def test_result_list_playbook(self):
        ctx = ansible_run()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '--playbook',
            six.text_type(ctx['playbook'].id)
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['result'].id)

    def test_result_list_non_existing_playbook(self):
        ansible_run()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_result_list_play(self):
        ctx = ansible_run()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', six.text_type(ctx['play'].id)])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['result'].id)

    def test_result_list_non_existing_play(self):
        ansible_run()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_result_list_task(self):
        ctx = ansible_run()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--task', six.text_type(ctx['task'].id)])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['result'].id)

    def test_result_list_non_existing_task(self):
        ansible_run()

        cmd = ara.cli.result.ResultList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--task', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_result_show(self):
        ctx = ansible_run()

        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx['result'].id)])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['result'].id)

    def test_result_show_non_existing(self):
        ansible_run()

        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)

    def test_result_show_long(self):
        ctx = ansible_run()

        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx['result'].id), '--long'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['result'].id)
        self.assertEqual(res[1][-1], jsonutils.dumps(ctx['result'].result))

    def test_result_show_long_non_existing(self):
        ansible_run()

        cmd = ara.cli.result.ResultShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0, '--long'])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLITask(TestAra):
    """ Tests for the ARA CLI task commands """
    def setUp(self):
        super(TestCLITask, self).setUp()

    def tearDown(self):
        super(TestCLITask, self).tearDown()

    def test_task_list_all(self):
        ctx = ansible_run()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--all'])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['task'].id)

    def test_task_list_play(self):
        ctx = ansible_run()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', six.text_type(ctx['play'].id)])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['task'].id)

    def test_task_list_non_existing_play(self):
        ansible_run()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--play', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_task_list_playbook(self):
        ctx = ansible_run()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([
            '--playbook',
            six.text_type(ctx['playbook'].id)
        ])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0][0], ctx['task'].id)

    def test_task_list_non_existing_playbook(self):
        ansible_run()

        cmd = ara.cli.task.TaskList(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args(['--playbook', six.text_type(9)])
        res = cmd.take_action(args)

        self.assertEqual(res[1], [])

    def test_task_show(self):
        ctx = ansible_run()

        cmd = ara.cli.task.TaskShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([six.text_type(ctx['task'].id)])
        res = cmd.take_action(args)

        self.assertEqual(res[1][0], ctx['task'].id)

    def test_task_show_non_existing(self):
        ansible_run()

        cmd = ara.cli.task.TaskShow(None, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([0])

        with self.assertRaises(RuntimeError):
            cmd.take_action(args)


class TestCLIGenerate(TestAra):
    """ Tests for the ARA CLI generate commands """
    def setUp(self):
        super(TestCLIGenerate, self).setUp()
        # Create a temporary directory for ara generate tests
        self.generate_dir = tempfile.mkdtemp(prefix='ara')

    def tearDown(self):
        super(TestCLIGenerate, self).tearDown()
        # Remove the temporary ara generate directory
        shutil.rmtree(self.generate_dir)

    def test_generate_empty_html(self):
        """ Ensures the application is still rendered gracefully """
        self.app.config['ARA_IGNORE_EMPTY_GENERATION'] = False
        dir = self.generate_dir
        shell = ara.shell.AraCli()
        shell.prepare_to_run_command(ara.cli.generate.GenerateHtml)
        cmd = ara.cli.generate.GenerateHtml(shell, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([dir])

        with pytest.warns(MissingURLGeneratorWarning) as warnings:
            cmd.take_action(args)

        # pytest 3.0 through 3.1 are backwards incompatible here
        if LooseVersion(pytest.__version__) >= LooseVersion('3.1.0'):
            cat = [item._category_name for item in warnings]
            self.assertTrue(any('MissingURLGeneratorWarning' in c
                                for c in cat))
        else:
            self.assertTrue(any(MissingURLGeneratorWarning == w.category
                                for w in warnings))

        paths = [
            os.path.join(dir, 'index.html'),
            os.path.join(dir, 'static'),
        ]

        for path in paths:
            self.assertTrue(os.path.exists(path))

    def test_generate_empty_html_with_ignore_empty_generation(self):
        """ Ensures the application is still rendered gracefully """
        self.app.config['ARA_IGNORE_EMPTY_GENERATION'] = True
        dir = self.generate_dir

        shell = ara.shell.AraCli()
        shell.prepare_to_run_command(ara.cli.generate.GenerateHtml)
        cmd = ara.cli.generate.GenerateHtml(shell, None)
        parser = cmd.get_parser('test')
        args = parser.parse_args([dir])
        cmd.take_action(args)

        paths = [
            os.path.join(dir, 'index.html'),
            os.path.join(dir, 'static'),
        ]

        for path in paths:
            self.assertTrue(os.path.exists(path))

    def test_generate_html_no_destination(self):
        """ Ensures generating without a destination fails """
        ansible_run()

        cmd = ara.cli.generate.GenerateHtml(None, None)
        parser = cmd.get_parser('test')

        with self.assertRaises(SystemExit):
            args = parser.parse_args([])
            cmd.take_action(args)

    def test_generate_html(self):
        """ Roughly ensures the expected files are generated properly """
        dir = self.generate_dir

        ctx = ansible_run()

        shell = ara.shell.AraCli()
        shell.prepare_to_run_command(ara.cli.generate.GenerateHtml)
        cmd = ara.cli.generate.GenerateHtml(shell, None)
        parser = cmd.get_parser('test')

        args = parser.parse_args([dir])
        cmd.take_action(args)

        file_id = ctx['task'].file_id
        host_id = ctx['host'].id
        result_id = ctx['result'].id
        paths = [
            os.path.join(dir, 'index.html'),
            os.path.join(dir, 'static'),
            os.path.join(dir, 'file/index.html'),
            os.path.join(dir, 'file/{0}'.format(file_id)),
            os.path.join(dir, 'host/index.html'),
            os.path.join(dir, 'host/{0}'.format(host_id)),
            os.path.join(dir, 'reports/index.html'),
            os.path.join(dir, 'result/index.html'),
            os.path.join(dir, 'result/{0}'.format(result_id))
        ]

        for path in paths:
            self.assertTrue(os.path.exists(path))

    def test_generate_html_for_playbook(self):
        """ Roughly ensures the expected files are generated properly """
        dir = self.generate_dir

        # Record two separate playbooks
        ctx = ansible_run()
        ansible_run()

        shell = ara.shell.AraCli()
        shell.prepare_to_run_command(ara.cli.generate.GenerateHtml)
        cmd = ara.cli.generate.GenerateHtml(shell, None)
        parser = cmd.get_parser('test')

        args = parser.parse_args([
            dir,
            '--playbook',
            six.text_type(ctx['playbook'].id)
        ])
        cmd.take_action(args)

        file_id = ctx['task'].file_id
        host_id = ctx['host'].id
        result_id = ctx['result'].id
        paths = [
            os.path.join(dir, 'index.html'),
            os.path.join(dir, 'static'),
            os.path.join(dir, 'file/index.html'),
            os.path.join(dir, 'file/{0}'.format(file_id)),
            os.path.join(dir, 'host/index.html'),
            os.path.join(dir, 'host/{0}'.format(host_id)),
            os.path.join(dir, 'reports/index.html'),
            os.path.join(dir, 'result/index.html'),
            os.path.join(dir, 'result/{0}'.format(result_id))
        ]

        for path in paths:
            self.assertTrue(os.path.exists(path))

        # Test that we effectively have two playbooks
        playbooks = m.Playbook.query.all()
        self.assertTrue(len(playbooks) == 2)

        # Retrieve the other playbook and validate that we haven't generated
        # files for it
        playbook_two = (m.Playbook.query
                        .filter(m.Playbook.id != ctx['playbook'].id).one())
        path = os.path.join(dir, 'playbook/{0}'.format(playbook_two.id))
        self.assertFalse(os.path.exists(path))

    def test_generate_junit(self):
        """ Roughly ensures the expected xml is generated properly """
        tdir = self.generate_dir

        ctx = ansible_run()
        cmd = ara.cli.generate.GenerateJunit(None, None)
        parser = cmd.get_parser('test')

        junit_file = '{tdir}/junit.xml'.format(tdir=tdir)
        args = parser.parse_args([junit_file])
        cmd.take_action(args)

        self.assertTrue(os.path.exists(junit_file))

        tasks = m.Task.query.all()
        tree = etree.parse(junit_file)
        self.assertEqual(tree.getroot().tag, "testsuites")
        self.assertEqual(tree.getroot()[0].tag, "testsuite")
        self.assertEqual(tree.getroot()[0][0].tag, "testcase")
        self.assertEqual(int(tree.getroot().get('tests')), len(tasks))
        self.assertEqual(int(tree.getroot().get('failures')),
                         ctx['host'].failed)

    def test_generate_junit_for_playbook(self):
        """ Roughly ensures the expected xml is generated properly """
        tdir = self.generate_dir

        # Record two separate playbooks
        ctx = ansible_run()
        ansible_run()
        cmd = ara.cli.generate.GenerateJunit(None, None)
        parser = cmd.get_parser('test')

        junit_file = "{tdir}/junit-playbook.xml".format(tdir=tdir)
        args = parser.parse_args([
            junit_file,
            '--playbook',
            six.text_type(ctx['playbook'].id)
        ])
        cmd.take_action(args)

        # Test that we effectively have two playbooks
        playbooks = m.Playbook.query.all()
        all_tasks = m.Task.query.all()
        tasks = (m.Task.query
                 .filter(m.Task.playbook_id == ctx['playbook'].id).all())
        self.assertEqual(len(playbooks), 2)
        self.assertNotEqual(len(all_tasks), len(tasks))

        self.assertTrue(os.path.exists(junit_file))

        tree = etree.parse(junit_file)
        self.assertEqual(tree.getroot().tag, "testsuites")
        self.assertEqual(tree.getroot()[0].tag, "testsuite")
        self.assertEqual(tree.getroot()[0][0].tag, "testcase")
        self.assertEqual(int(tree.getroot().get('tests')), len(tasks))

    def test_generate_subunit(self):
        """ Roughly ensures the expected subunit is generated properly """
        tdir = self.generate_dir

        ansible_run()
        cmd = ara.cli.generate.GenerateSubunit(None, None)
        parser = cmd.get_parser('test')

        subunit_file = os.path.join(tdir, 'test.subunit')
        subunit_dir = os.path.join(tdir, 'subunit_dir')
        args = parser.parse_args([subunit_file])
        cmd.take_action(args)

        self.assertTrue(os.path.exists(subunit_file))
        # Dump the subunit binary stream to some files we can read and assert
        with open(subunit_file, 'r') as f:
            to_disk(['-d', subunit_dir], stdin=f)

        # Get *.json files, load them and test them
        data = []
        testfiles = glob("%s/%s" % (subunit_dir, '*/*.json'))
        for testfile in testfiles:
            with open(testfile, 'rb') as f:
                data.append(jsonutils.load(f))

        keys = ['status', 'tags', 'stop', 'start', 'details', 'id']
        for result in data:
            # Test that we have the expected keys, no more, no less
            for key in keys:
                self.assertTrue(key in result.keys())
            for key in result.keys():
                self.assertTrue(key in keys)

        # Get non-json files, load them and test them
        data = []
        testfiles = [fn for fn in glob("%s/%s" % (subunit_dir, '*/*'))
                     if not os.path.basename(fn).endswith('json')]
        for testfile in testfiles:
            with open(testfile, 'rb') as f:
                data.append(jsonutils.load(f))

        keys = ['host', 'playbook_id', 'playbook_path', 'play_name',
                'task_action', 'task_action_lineno', 'task_id', 'task_name',
                'task_path']
        for result in data:
            # Test that we have the expected keys, no more, no less
            for key in keys:
                self.assertTrue(key in result.keys())
            for key in result.keys():
                self.assertTrue(key in keys)

            # Test that we have matching data for playbook records
            playbook = m.Playbook.query.get(result['playbook_id'])
            self.assertEqual(playbook.id, result['playbook_id'])
            self.assertEqual(playbook.path, result['playbook_path'])

            # Test that we have matchin gdata for task records
            task = m.Task.query.get(result['task_id'])
            self.assertEqual(task.id, result['task_id'])
            self.assertEqual(task.action, result['task_action'])
            self.assertEqual(task.file.path, result['task_path'])
            self.assertEqual(task.lineno, result['task_action_lineno'])
            self.assertEqual(task.name, result['task_name'])
