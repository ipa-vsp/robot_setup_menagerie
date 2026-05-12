from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'isaac_assembler'

def get_data_files():
    data_files = [
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        # Install scripts into the lib directory so they can be run by ros2 run
        (os.path.join('lib', package_name), ['scripts/assemble_techtory_fr3.py']),
    ]
    
    for directory in ['assets', 'scripts']:
        for root, dirs, files in os.walk(directory):
            if files:
                dest = os.path.join('share', package_name, root)
                src = [os.path.join(root, f) for f in files]
                data_files.append((dest, src))
            
    return data_files

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=get_data_files(),
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ipa326',
    maintainer_email='ipa326@todo.todo',
    description='Package for assembling robots in Isaac Sim',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Keeping console_scripts but also installing raw script as fallback
            'assemble_techtory_fr3 = isaac_assembler.assemble_techtory_fr3:main'
        ],
    },
)
