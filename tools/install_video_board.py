#!/usr/bin/env python3
"""Install only the requested read-only native board; never register a launch agent."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import plistlib
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    home=Path.home();destination=home/'Applications/Video Team Board.app'
    source=ROOT/'runtime/kanban';stamp=dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    archive=home/'.codex/archive'/('video_team_board_'+stamp)
    with tempfile.TemporaryDirectory(prefix='video-team-board-build-') as td:
        built=Path(td)/'Video Team Board.app';resources=built/'Contents/Resources';binary=built/'Contents/MacOS/VideoTeamBoard'
        resources.mkdir(parents=True);binary.parent.mkdir(parents=True)
        subprocess.run(['/usr/bin/swiftc',str(source/'Board.swift'),'-o',str(binary),'-framework','AppKit','-framework','WebKit'],check=True)
        for name in ('board.html','snapshot.py'):shutil.copy2(source/name,resources/name)
        with (built/'Contents/Info.plist').open('wb') as f:plistlib.dump({'CFBundleIdentifier':'local.gnudas.video-team-board','CFBundleName':'Video Team Board','CFBundleExecutable':'VideoTeamBoard','CFBundlePackageType':'APPL','CFBundleVersion':'1','LSUIElement':True,'NSHighResolutionCapable':True},f)
        subprocess.run(['/usr/bin/codesign','--force','--sign','-',str(built)],check=True)
        destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists():archive.mkdir(parents=True,exist_ok=True);shutil.move(str(destination),archive/destination.name)
        shutil.copytree(built,destination)
    launcher=home/'.local/bin/video-team-board';launcher.parent.mkdir(parents=True,exist_ok=True)
    if launcher.exists():archive.mkdir(parents=True,exist_ok=True);shutil.copy2(launcher,archive/'video-team-board')
    launcher.write_text('''#!/usr/bin/python3
import argparse,json,os,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--project',type=Path);a=p.parse_args()
home=Path.home()
if a.project:
 root=(home/'Documents/Codex/video-team-runtime').resolve();project=a.project.resolve()
 if project.parent!=root or not (project/'manifest.json').is_file():p.error('registered runtime project required')
 config=home/'.codex/video-team-board/selection.json';config.parent.mkdir(parents=True,exist_ok=True)
 temporary=config.with_suffix('.tmp');temporary.write_text(json.dumps({'project':project.name}));os.replace(temporary,config)
subprocess.run(['/usr/bin/open','-g',str(home/'Applications/Video Team Board.app')],check=True)
''');launcher.chmod(0o755)
    print(json.dumps({'ok':True,'app':str(destination),'launcher':str(launcher),'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir() if p.is_file()},'launch_agent_created':False,'scheduler_created':False},indent=2))
if __name__=='__main__':main()
