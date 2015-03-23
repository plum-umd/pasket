#!/usr/bin/env python

import os
import sys
import unittest
import logging
import subprocess
import shutil

from string import capwords

root_dir = os.path.join(os.path.dirname(__file__), "..")

lib_dir = os.path.join(root_dir, "lib")
junit_jar = os.path.join(lib_dir, "junit-4.11.jar")
os.environ["CLASSPATH"] = junit_jar

res_dir = os.path.join(root_dir, "result")
smpl_dir = os.path.join(root_dir, "sample")
tmpl_dir = os.path.join(root_dir, "template")
ex_dir = os.path.join(root_dir, "example")
res_java = os.path.join(res_dir, "java")

sys.path.insert(0, root_dir)
import pasket

class TestPatterns(unittest.TestCase):
    
    def setUp(self):
        self.cwd = os.getcwd()
    
    def tearDown(self):
        os.chdir(self.cwd)
    
    def sanity_check(self, p, names):
        for name in names:
            # Copy unit test into output directory
            test = name.capitalize() + "Test"
            main = capwords(name, "_").replace("_", "")
            sani = "SanityChecker"
            samp_proc = "SampleProcessor"
            if (p == "pattern"):
                #shutil.copy(os.path.join(tmpl_dir, "pattern", "test", test+".java"), res_java)
                shutil.copy(os.path.join(tmpl_dir, "pattern", "test", name, sani+".java"), res_java)
                test_folder = os.path.join(tmpl_dir, "pattern", "test")
            elif (p == "gui"):
                #shutil.copy(os.path.join(tmpl_dir, "app", "gui", "test", test+".java"), res_java)
                #shutil.copy(os.path.join(tmpl_dir, "app", "gui", "test", main+".java"), res_java)
                shutil.copy(os.path.join(tmpl_dir, "app", "gui", "test", name, sani+".java"), res_java)
                shutil.copy(os.path.join(tmpl_dir, "app", "gui", "test", samp_proc+".java"), res_java)
                test_folder = os.path.join(tmpl_dir, "app", "gui", "test", name)
            for filename in os.listdir(test_folder):
                file = os.path.join(test_folder, filename)
                if (not os.path.isdir(file)):
                    shutil.copy(file, res_java)
                else:
                    dest = os.path.join(res_java, filename)
                    if os.path.exists(dest): shutil.rmtree(dest)
                    shutil.copytree(file, dest)
            
            # Compile Java output and unit test
            os.chdir(res_dir)
            subprocess.call(["ant", "-Ddemo="+'_'.join(names)])
            
            # Run unit tests
            subprocess.call(["ant", "run", "-Dtest="+test])
            
            os.chdir("..")
    
    def run_pasket(self, p, names):
        # Run translation to sketch and then run sketch
        if (p == "pattern"):
            smpl = [os.path.join(smpl_dir, p, names)]
            tmpl = [os.path.join(tmpl_dir, p, names)]
        elif (p == "gui"):
            smpl = []
            tmpl = [] #[os.path.join(tmpl_dir, "app", p, name), os.path.join(tmpl_dir, "gui")]

        pasket.no_encoding()
        pasket.no_sketch()
        pasket.main(p, smpl, tmpl, names, res_dir)
        
        # Copy java directory to pasket directory
        os.chdir(res_dir)
        subprocess.call(["./rename-gui.sh"])
        os.chdir("..")
    
    def check_word_finder(self, p, names):
      name = "WordFinder"
      test = name + "Tester"
      samp_proc = "SampleProcessor"
      shutil.copy(os.path.join(ex_dir, name, "PasketTester.java"), res_java)
      shutil.copy(os.path.join(ex_dir, name, "WordFinder.es"), res_java)
      shutil.copy(os.path.join(ex_dir, name, test+".java"), res_java)
      shutil.copytree(os.path.join(ex_dir, name, "src", "words"), os.path.join(res_java, "words"))
      
      # Compile Java output and unit test
      os.chdir(res_dir)
      subprocess.call(["ant", "-Ddemo="+'_'.join(names)])
    
      # Run unit tests
      subprocess.call(["ant", "run", "-Dtest="+test])
    
    
    def check_examples(self, p, names):
      self.check_word_finder(p,names)
    
    def test_pattern(self):
        p, names = sys.argv[1], sys.argv[2:]
        self.run_pasket(p,names)
        self.sanity_check(p,names)
        #self.check_examples(p,names)
        self.assertTrue(True)
    
    @unittest.skip("not working yet")
    def test_builder(self):
        self.gen_pattern("builder")
        self.assertTrue(True)
    
    @unittest.skip("not working yet")
    def test_proxy(self):
        self.gen_pattern("proxy")
        self.assertTrue(True)
    
    @unittest.skip("not working yet")  
    def test_singleton(self):
        self.gen_pattern("singleton")
        self.assertTrue(True)
    
    @unittest.skip("not working yet")  
    def test_state(self):
        self.gen_pattern("state")
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main(argv=[sys.argv[1]])

