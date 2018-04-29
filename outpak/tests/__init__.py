import os
from unittest import TestCase

from outpak.config import OutpakConfig

PAK = """
version: "1"
github_key: TEST_GIT_TOKEN_PAK
bitbucket_key: TEST_BIT_TOKEN_PAK
env_key: TEST_ENV_PAK
index_url: https://user:key@privatepypi.com
envs:
  dev:
    key_value: development
    use_virtual: True
    clone_dir: /tmp
    files:
      - requirements.txt
    constraints:
      - constraints.txt
  docker:
    key_value: docker
    clone_dir: /opt/src
    files:
      - requirements.txt
  private:
    key_value: private
    clone_dir: /tmp
    index_url: https://user:key@privatepypi2.com
    extra_indexes:
      - https://user:key@privatepypi3.com
      - https://user:key@privatepypi4.com
    files:
      - requirements.txt
"""

REQ = """
# This is a comment

-r requirements_test.txt
-c constraints_test.txt
SomeProject
SomeProject == 1.3
SomeProject >=1.2,<.2.0
SomeProject[foo, bar]
SomeProject~=1.4.2
SomeProject ==5.4 ; python_version < '2.7'
SomeProject; sys_platform == 'win32'
SomeProject[foo]>=2.18.1  # another comment

FooProject >= 1.2 --global-option="--no-user-cfg" \
                  --install-option="--prefix='/usr/local'" \
                  --install-option="--no-compile"

https://git.myproject.org/MyProject#egg=MyProject
https://git.myproject.org/MyProject@commit123#egg=MyProject

git://git.myproject.org/MyProject#egg=MyProject
git+http://git.myproject.org/MyProject#egg=MyProject
git+https://git.myproject.org/MyProject#egg=MyProject
git+ssh://git.myproject.org/MyProject#egg=MyProject
git+git://git.myproject.org/MyProject#egg=MyProject
git+file://git.myproject.org/MyProject#egg=MyProject

-e git+git@git.myproject.org:MyProject#egg=MyProject
-e git+https@https://github.com:MyProject#egg=MyProject
-e git+git@github.com:org/:MyProject#egg=MyProject

git://git.myproject.org/MyProject.git@master#egg=MyProject
git://git.myproject.org/MyProject.git@v1.0#egg=MyProject
git://git.myproject.org/MyProject.git@da39a3ee5e6b4b0d3255bfef95601890afd80709#egg=MyProject

hg+http://hg.myproject.org/MyProject#egg=MyProject
hg+https://hg.myproject.org/MyProject#egg=MyProject
hg+ssh://hg.myproject.org/MyProject#egg=MyProject

--index_url https://user:key@mypip1.com
hg+http://hg.myproject.org/MyProject@da39a3ee5e6b#egg=MyProject
hg+http://hg.myproject.org/MyProject@2019#egg=MyProject
hg+http://hg.myproject.org/MyProject@v1.0#egg=MyProject
hg+http://hg.myproject.org/MyProject@special_feature#egg=MyProject

svn+svn://svn.myproject.org/svn/MyProject#egg=MyProject
svn+http://svn.myproject.org/svn/MyProject/trunk@2019#egg=MyProject

bzr+http://bzr.myproject.org/MyProject/trunk#egg=MyProject
bzr+sftp://user@myproject.org/MyProject/trunk#egg=MyProject
bzr+ssh://user@myproject.org/MyProject/trunk#egg=MyProject
bzr+ftp://user@myproject.org/MyProject/trunk#egg=MyProject
bzr+lp:MyProject#egg=MyProject
bzr+https://bzr.myproject.org/MyProject/trunk@2019#egg=MyProject
bzr+http://bzr.myproject.org/MyProject/trunk@v1.0#egg=MyProject

-e ./packages/my_package

--extra-indexes https://user:key@mypip2.com
SomeProject == 1.3
SomeProject >=1.2,<.2.0
--no-binary git+http://git.myproject.org/MyProject#egg=MyProject
--only-binary git+https://git.myproject.org/MyProject#egg=MyProject
--no-index
--find-links /my/local/archives
--find-links http://some.archives.com/archives
"""

class OutpakTestBase(TestCase):
    def setUp(self):
        """setUp."""
        super(OutpakTestBase, self).setUp()
        self.path = "/tmp/pak.yml"
        self.config = OutpakConfig(self.path, {'--config': None, '--quiet': None})
        self._load_from_file()

    def tearDown(self):
        """tearDown."""
        if os.getenv('TEST_ENV_PAK'):
            del os.environ['TEST_ENV_PAK']
        if os.getenv('TEST_GIT_TOKEN_PAK'):
            del os.environ['TEST_GIT_TOKEN_PAK']
        if os.getenv('TEST_BIT_TOKEN_PAK'):
            del os.environ['TEST_BIT_TOKEN_PAK']
        if os.path.exists(self.path):
            os.remove(self.path)
        if os.path.exists('/tmp/requirements.txt'):
            os.remove('/tmp/requirements.txt')

    def _load_from_file(self):
        with open(self.path, "w") as file:
            file.write(PAK)
        self.config._load_from_yaml()
        os.remove(self.path)