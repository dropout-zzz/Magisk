#!/usr/bin/env python3

import argparse
import os, os.path
import hashlib
import urllib.request
import shutil
import zipfile
import tempfile
import subprocess
import json
import re
import contextlib
import typing
from os import environ, lstat
from os.path import dirname, abspath
from stat import S_IFREG, S_IFDIR, S_IFLNK, S_IFMT, S_IMODE
from subprocess import STDOUT, PIPE
from dataclasses import dataclass

TEST_DATA = os.path.join(environ['HOME'], '.dropout', 'blossom_ofox.img')
TEST_DATA_INFO = {
  'path': TEST_DATA,
  'md5': '31c1f500f870cc3a4866d1121ab90e37', 'size': 67108864
}

def validate_file(path: str, *, md5: str, size: int):
  got = os.path.getsize(path)
  assert got == size, f'file {path!r} has wrong size (expects {size} bytes, got {got})'

  with open(path, 'rb') as f:
    assert hashlib.file_digest(f, 'md5').hexdigest() == md5, f'file {path!r} corrupted (expect MD5: {md5})'

def fetch_test_data():
  os.makedirs(dirname(TEST_DATA), exist_ok=True)

  with urllib.request.urlopen('https://sourceforge.net/projects/crdroid/files/'
                              'blossom/12.x/recovery-ofox/'
                              'OrangeFox-R12.0-Unofficial-blossom.zip') as resp:
    with tempfile.TemporaryFile() as tmp:
      shutil.copyfileobj(resp, tmp)

      with zipfile.ZipFile(tmp) as zf:
        with zf.open('recovery.img') as f:
          with open(TEST_DATA, 'wb') as f2:
            shutil.copyfileobj(f, f2)

  validate_file(**TEST_DATA_INFO)

def ensure_test_data():
  if os.path.exists(TEST_DATA):
    try:
      validate_file(**TEST_DATA_INFO)
    except AssertionError:
      print('bad test image in cache? re-downloading...')
      fetch_test_data()
  else:
    print('downloading test image...')
    fetch_test_data()

class TestContext(contextlib.AbstractContextManager):
  """remembers previously executed cmds via self.magiskboot()
     with their outputs, prints them on a failed run.

     when used with a "with" statement, info about all
      previous cmds associated with this context will be
     printed automatically if an AssertionError was occured
     within the "with" block. the exception is not suppressed."""

  def __init__(self, mb_exe: str):
    """create new ctx with specified path to magiskboot program."""

    self.__magiskboot = mb_exe
    self.__run_args: dict[str, typing.Any] = {}
    self.__prev_cmds: list[subprocess.CompletedProcess] = []

  def __enter__(self):
    return self

  def __print_prev_cmds(self):
    for p in self.__prev_cmds:
      print(p.args)
      print(p.stdout)
    self.__prev_cmds.clear()

  def __exit__(self, etype, exc, tb):
    if etype is AssertionError:
      self.__print_prev_cmds()

  def set_run_args(self, x: dict[str, typing.Any]):
    self.__run_args = x.copy()

  def magiskboot(self, args, /, **run_args) -> str:
    """run a magiskboot command.

       overall usage is almost the same as subprocess.run(),
       except retval is full output in string.

       if the program fails, args and outputs of all previous
        cmds plus this cmd will be printed in order they were
        called, then an exception is raised.

       callers shouldn't modify output-capturing related options."""

    p = subprocess.run([self.__magiskboot, *args],
                       stdout=PIPE, stderr=STDOUT, text=True,
                       **self.__run_args, **run_args)
    if p.returncode == 0:
      self.__prev_cmds.append(p)
      return p.stdout

    self.__print_prev_cmds()
    print(subprocess.CalledProcessError(p.returncode, p.args))
    print(p.stdout)

    raise AssertionError('last invocation failed')

def test_unpack_repack_1(ctx: TestContext, /):
  """try to produce an identical image by skipping compressions."""

  with tempfile.TemporaryDirectory() as tmpdir:
    ctx.set_run_args({'cwd': tmpdir})
    ctx.magiskboot(['unpack', '-n', TEST_DATA])

    with tempfile.NamedTemporaryFile(suffix='.img') as tmp:
      ctx.magiskboot(['repack', '-n', TEST_DATA, tmp.name])
      validate_file(**{**TEST_DATA_INFO, 'path': tmp.name})

    ctx.magiskboot(['cleanup'])
    dirents = os.listdir(tmpdir)
    assert len(dirents) == 0, f'did not clean: {dirents}'

def test_unpack_repack_2(ctx: TestContext, /, *, work: str):
  """another but using the compression / decompression path."""

  ctx.set_run_args({'cwd': work})

  ctx.magiskboot(['unpack', TEST_DATA])
  ctx.magiskboot(['repack', TEST_DATA, './new.img'])
  ctx.magiskboot(['cleanup'])

  out = ctx.magiskboot(['unpack', './new.img'])
  assert re.fullmatch('''\
Parsing boot image: \\[\\./new.img\\]
HEADER_VER      \\[2\\]
KERNEL_SZ       \\[\\d+\\]
RAMDISK_SZ      \\[\\d+\\]
SECOND_SZ       \\[0\\]
RECOV_DTBO_SZ   \\[148432\\]
DTB_SZ          \\[127044\\]
OS_VERSION      \\[99\\.87\\.36\\]
OS_PATCH_LEVEL  \\[2127-12\\]
PAGESIZE        \\[2048\\]
NAME            \\[\\]
CMDLINE         \\[bootopt=64S3,32N2,64N2 androidboot\\.selinux=permissive androidboot\\.init_fatal_reboot_target=recovery buildvariant=eng\\]
CHECKSUM        \\[[0-9a-f]{64}\\]
KERNEL_FMT      \\[gzip\\]
RAMDISK_FMT     \\[gzip\\]
VBMETA
''', out) is not None, 'bad header output'

  validate_file(f'{work}/dtb', md5='dfdf1149f194a9d6a0143f994dd131ae', size=127044)
  validate_file(f'{work}/kernel', md5='89d529f55768c6b3f56c66b95c7a3cab', size=25991184)
  validate_file(f'{work}/ramdisk.cpio', md5='5a38bdc2e2f086987af2d85dd9dfd125', size=84336384)
  validate_file(f'{work}/recovery_dtbo', md5='0fe6f35d73cdf8872ca0a8cdc90ce44c', size=148432)

def test_fdt(ctx: TestContext, /, *, work: str):
  out = ctx.magiskboot(['dtb', './dtb', 'print'], cwd=work)

  with open('testdata_dt_blossom.dump', 'r') as f:
    assert out == f.read(), 'bad device-tree output'

def test_hexpatch(ctx: TestContext, /):
  a = bytes.fromhex('0011223344deadbeef5566778899')
  b = bytes.fromhex('0011223344f00dcafe5566778899')

  with tempfile.NamedTemporaryFile(suffix='.bin') as tmp:
    tmp.write(a); tmp.flush(); tmp.seek(0)
    ctx.magiskboot(['hexpatch', tmp.name, 'deadbeef', 'f00dcafe'])
    data = tmp.read()
    assert data == b, f'result corrupted: {data.hex()}'

def expect_mode(*, path: str, fmt: int, perm_s: typing.Optional[str] = None):
  WHAT = {
    S_IFREG: 'a regular file',
    S_IFDIR: 'a directory',
    S_IFLNK: 'a symlink',
  }

  mode = lstat(path).st_mode
  x = S_IFMT(mode)
  assert x == fmt, f'expects {path!r} to be {WHAT[fmt]} (got {WHAT[x]})'

  if perm_s is None:
    return

  perm = S_IMODE(mode)
  assert perm == int(perm_s, 8), f'expects {path!r} to be {perm_s} (got {perm:04o})'

def test_cpio(ctx: TestContext, /, *, work: str):
  with open('ramfs_contents_blossom_ofox.json', 'r') as f:
    m = json.load(f)

  with tempfile.TemporaryDirectory() as tmpdir:
    ctx.magiskboot(['cpio', f'{work}/ramdisk.cpio', 'extract'], cwd=tmpdir)

    for dir_ent in m['dirs']:
      path = os.path.join(tmpdir, dir_ent['path'])
      expect_mode(path=path, fmt=S_IFDIR, perm_s=dir_ent['perm'])

    for link_ent in m['links']:
      path = os.path.join(tmpdir, link_ent['path'])
      expect_mode(path=path, fmt=S_IFLNK)

      target = os.readlink(path)
      expect = link_ent['target']
      assert target == expect, f'expects {path!r} to point to {expect!r} (got {target!r})'

    for file_ent in m['files']:
      path = os.path.join(tmpdir, file_ent['path'])

      expect_mode(path=path, fmt=S_IFREG, perm_s=file_ent['perm'])
      validate_file(path, md5=file_ent['md5'], size=file_ent['size'])

@dataclass
class ContextTemplate:
  # path to magiskboot binary
  mb_exe: str

def run_test(templ: ContextTemplate, /, *, what: str, fn, **kwargs):
  print(f'- testing {what}...')
  with TestContext(mb_exe=templ.mb_exe) as ctx:
    fn(ctx, **kwargs)

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument('executable', type=abspath, help='full path to magiskboot program')
  args = ap.parse_args()

  os.chdir(dirname(__file__))

  ensure_test_data()

  templ = ContextTemplate(mb_exe=args.executable)

  print('todo: add payload.bin and AVB tests')

  run_test(templ,
           what='hexpatch command',
           fn=test_hexpatch)

  run_test(templ,
           what='unpack / repack (w/o decompression)',
           fn=test_unpack_repack_1)

  with tempfile.TemporaryDirectory() as tmpdir:
    run_test(templ,
             what='unpack / repack (w/ compressions)',
             fn=test_unpack_repack_2,
             work=tmpdir)

    run_test(templ,
             what='"dtb print" command',
             fn=test_fdt,
             work=tmpdir)

    run_test(templ,
             what='"cpio" extract command',
             fn=test_cpio,
             work=tmpdir)

  print('all tests succeeded.')

main()
