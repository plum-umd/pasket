package rasket.test;

import org.junit.Assert;

import java.nio.file.*;
import java.io.*;
import java.util.*;
import java.lang.reflect.*;
//import pasket.java.awt.*;
//import pasket.javax.swing.*;
//import pasket.java.awt.event.*;


public class LogChecker {
    /*
    static SwingEventHandler seh;
    public static SwingEventHandler getEventHandler(AdaptedButtonDemo abd) {
        if (seh == null)
            seh = new SwingEventHandler(abd);
        return seh;
    }
    */
    
    public static void main(String[] args)
    throws ClassNotFoundException, NoSuchMethodException,
    IllegalAccessException, InvocationTargetException,
    IOException, InterruptedException {
        /*Path root_dir = Paths.get(System.getProperty("user.dir")).getParent();
        Path res_dir = root_dir.resolve("result");
        Path smpl_dir = root_dir.resolve("sample/pattern/" + demo);
        Path tmpl_dir = root_dir.resolve("template/pattern/" + demo);
        if (demo.endsWith("demo")) {
            smpl_dir = root_dir.resolve("sample/gui/" + demo);
            tmpl_dir = root_dir.resolve("template/app/gui/" + demo);
        }*/
        
        String demo = args[0];

        File test_temp = new File("rasket/log/ObserverTester.txt");
        SampleProcessor.generate("ObserverTester", test_temp);
        
        File sim_temp = new File("rasket/log/ObserverSimulator.txt");
        SampleProcessor.generate("ObserverSimulator", sim_temp);
        
	System.out.println("Checking log file: " + test_temp);

        Queue<String> records = getInfo(sim_temp, demo);
	if (records == null)
            return;
        //temp.delete();

	
        //Queue<String> orig_sample = toQueue(child);
        Queue<String> mcs = extractMethodCalls(test_temp, demo);
        Queue<String> mcalls = SampleProcessor.process(mcs);
        System.out.println("[debug] mcalls: " + mcalls);
                
        
        //get the generated log for the current sample
        Queue<String> curr_log = new ArrayDeque<String>();
        String[] recarray = new String[records.size()];
        recarray = records.toArray(recarray);
        int i = 0;
        String simulator;
        simulator = "ObserverSimulator.main";

	for (int m = 0; m < recarray.length; m++) {
            String s = recarray[i++].trim().replaceAll("Simulator", "Tester");
	    s = s.replaceAll("RealObserver", "MockObserver");
	    s = s.replaceAll("javax.swing.JButton", "rasket.JButton");
	    curr_log.add(s);
	}
	/*
        while (!recarray[i++].contains(simulator)) {
	    System.out.println(recarray[i]);
            continue;
	}
		
        while (!recarray[i].contains(simulator)){
            curr_log.add(recarray[i++].trim().replaceAll("Simulator", "Tester"));
        }
        */      
        //assert that the original sample is included in the generated log
        System.out.println("[debug] curr_log: " + curr_log);
        Assert.assertTrue("failure", included(mcalls, curr_log));
        System.out.println("Pass!");
        
        /*ProcessBuilder grepBuilder = new ProcessBuilder("grep", "'INFO: '", "temp.txt");
         grepBuilder.directory(new File("."));
         grepBuilder.inheritIO();
         Process grep = grepBuilder.start();
         grep.waitFor();*/
        
        
        
        
        /*File[] samples = smpl_dir.toFile().listFiles();
         for (File smpl : samples) {
         if (smpl.getName().startsWith("sample")) {
         String scenName = smpl.getName().substring(6, 7);
         Method scenario = Class.forName("Main").getMethod("main" + scenName);
         Assert.assertTrue("failure", compare(scenario));
         }
         }*/
    }
    
    //check if the shorter queue is included in the longer queue
    public static boolean included(Queue<String> shorter, Queue<String> longer) {
        Map<String, Integer> h1 = new HashMap<String, Integer>();
        Map<String, Integer> h2 = new HashMap<String, Integer>();
        while (! shorter.isEmpty()) {
            String curr = shorter.remove();
            while (! longer.isEmpty()) {
                if (compare(curr, longer.peek(), h1, h2)) break;
                longer.remove();
            }
            if (longer.isEmpty()) {
                System.out.println("A method call cannot be matched:");
                System.out.println(curr + " !");
                break;
            }
            //System.out.println(curr + " matched!");
        }
        
        return (!longer.isEmpty());
    }
    
    //check if the two logs are consistent w.r.t. the corresponding hash map
    public static boolean compare(String first, String second, Map<String, Integer> h1, Map<String, Integer> h2) {
        second = second.replaceAll("\"", "");
        String[] hash1 = getHash(first);
        String[] hash2 = getHash(second);
        if (hash1.length != hash2.length) return false;
        else if (! getPrototype(first, hash1).equals(getPrototype(second, hash2))) {
            //System.out.println("Mismatched prototype: " + getPrototype(first, hash1) + " vs. " + getPrototype(second, hash2));
            return false;
        }
        else {
            //System.out.println("Matched prototype: " + getPrototype(first, hash1) + " vs. " + getPrototype(second, hash2));
            for (int i = 0; i < hash1.length; i++) {
                if (! h1.containsKey(hash1[i]))
                    h1.put(hash1[i], new Integer(h1.size()));
                first = first.replaceFirst("@" + hash1[i], "@obj_" + h1.get(hash1[i]));
                if (! h2.containsKey(hash2[i]))
                    h2.put(hash2[i], new Integer(h2.size()));
                second = second.replaceFirst("@" + hash2[i], "@obj_" + h2.get(hash2[i]));
                
                /*if (h1.containsKey(hash1[i])) {
                 if (h1.get(hash1[i]).intValue() != h2.get(hash2[i]).intValue()) return false;
                 }
                 else {
                 if (h2.containsKey(hash2[i])) return false;
                 h1.put(hash1[i], new Integer(h1.size()));
                 h2.put(hash2[i], new Integer(h2.size()));
                 }*/
            }
            return first.equals(second);
        }
    }
    
    public static String getPrototype(String orig, String[] hash) {
        for (int i = 0; i < hash.length; i++) {
            orig = orig.replaceFirst("@" + hash[i], "@obj");
        }
        return orig;
    }
    
    public static String[] getHash(String log) {
        ArrayList<String> code =  new ArrayList<String>();
        
        int index = log.indexOf("@");
        while (index >= 0) {
            int nextBrkt = log.length();
            int idx1 = log.indexOf(")", index);
            int idx2 = log.indexOf(",", index);
            int idx3 = log.indexOf("]", index);
            if (idx1 >= 0) nextBrkt = Math.min(nextBrkt, idx1);
            if (idx2 >= 0) nextBrkt = Math.min(nextBrkt, idx2);
            if (idx3 >= 0) nextBrkt = Math.min(nextBrkt, idx3);
            code.add(log.substring(index + 1, nextBrkt));
            index = log.indexOf("@", nextBrkt);
        }
        String[] result = new String[code.size()];
        return code.toArray(result);
    }
    
    public static Queue<String> getInfo(File f, String pattern)
    throws FileNotFoundException {
        Queue<String> output = new ArrayDeque<String>();
        
        Scanner sc = new Scanner(f);
        while (sc.hasNextLine()) {
            String curr = sc.nextLine();
            if (curr.contains("Exception in thread")) {
                System.out.println("Exception thrown!");
                return null;
            }
            if (curr.contains("INFO: ")) output.add(curr.substring(6).trim().replaceAll("patterns." + pattern + ".", "").replaceAll("pasket.", ""));
        }
        return output;
    }
    
    // store a sample to a string queue
    public Queue<String> toQueue(File file)
    throws FileNotFoundException, IOException {
        Queue<String> el = new ArrayDeque<String>();
        
        Scanner reader = new Scanner(file);
        while (reader.hasNextLine()) {
            String curr = reader.nextLine();
            if (isEvent(curr)) el.add(curr);
        }
        return el;
    }
    
    // extract an event queue from a file
    public Queue<String> extractEvents(File file, String pattern)
    throws FileNotFoundException, IOException {
        Queue<String> el = new ArrayDeque<String>();
        
        Scanner reader = new Scanner(file);
        while (reader.hasNextLine()) {
            String curr = reader.nextLine();
            if (isEvent(curr)) el.add(curr.trim().replaceAll("patterns." + pattern + ".", ""));
        }
        
        return el;
    }
    
    public boolean isEvent(String s) {
        return s.contains("Date.Date");
    }
    
    //extract method calls from a file
    public static Queue<String> extractMethodCalls(File file, String pattern)
    throws FileNotFoundException, IOException {
        Queue<String> el = new ArrayDeque<String>();
        
        Scanner reader = new Scanner(file);
        while (reader.hasNextLine()) {
            String curr = reader.nextLine();
            //skip commented items
            if (curr.contains("//")) continue;
	    if (! curr.startsWith("INFO")) continue;
	    if (curr.contains("JButton.JButton")) continue;
            String l = curr.trim();
            el.add(l.replaceAll("\"", "").replaceAll("INFO: ", ""));
        }
        
        return el;
    }
    
    public static boolean isMethodCall(String s, String pattern) {
        if (pattern.equals("observer"))
            return (s.contains("addObserver") || s.contains("dateChanged"));
        else if (pattern.endsWith("demo"))
            return ((s.contains("javax.swing") || s.contains("java.awt"))
                    && (! s.contains("invokeLater(")) && (! s.contains("pack"))
			//&& (! s.contains("setDefaultCloseOperation"))
			//&& (! s.contains("setVerticalTextPosition"))
			//&& (! s.contains("setHorizontalTextPosition"))
			//&& (! s.contains("setMnemonic"))
			//&& (! s.contains("setEnabled"))
			//&& (! s.contains("setToolTipText"))
			//&& (! s.contains("setContentPane"))
			//&& (! s.contains("setVisible")) 
			 );
        else return false;
    }
    
    /*public Event getEvent(String s) {
     String dt = s.substring(s.indexOf("(")+1, s.indexOf(")"));
     Event e = new Event();
     e.kind = 0;
     e.date = new Date(Integer.parseInt(dt));
     return e;
     }*/
    
}


