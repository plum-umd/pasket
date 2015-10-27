import org.junit.Assert;

import java.nio.file.*;
import java.io.*;
import java.util.*;
import java.lang.reflect.*;
import pasket.java.awt.*;
import pasket.javax.swing.*;
import pasket.java.awt.event.*;
import pasket.javax.swing.colorchooser.*;
import pasket.javax.swing.event.*;


class SwingEventHandler implements EventHandler {
    AdaptedColorChooserDemo demo;
    public SwingEventHandler(AdaptedColorChooserDemo abd) {
        demo = abd;
    }
    
    public void handleEvent (String line) {
        if (line.endsWith("doClick()")) {
            String action = line.substring(0, line.indexOf("."));
            DefaultColorSelectionModel temp = (DefaultColorSelectionModel)demo.tcc.getSelectionModel();
            ChangeEvent evt = new ChangeEvent(temp);
            /*
            ActionListener[] listeners = temp.getActionListeners();
            for (int i = 0; i < listeners.length; i++) {
                listeners[i].actionPerformed(evt);
            }*/
            temp.fireStateChanged(evt);
        }
        return;
    }
    
    private JButton getButton(String command) {
        if (command.equals("$Black")) return null;
        else return null;
    }
}

public class SanityChecker {
    static SwingEventHandler seh;
    public static SwingEventHandler getEventHandler(AdaptedColorChooserDemo abd) {
        if (seh == null)
            seh = new SwingEventHandler(abd);
        return seh;
    }
    
    public void sanityCheck(String demo, int num_es)
    throws ClassNotFoundException, NoSuchMethodException,
    IllegalAccessException, InvocationTargetException,
    IOException, InterruptedException {
        Path root_dir = Paths.get(System.getProperty("user.dir")).getParent();
        Path res_dir = root_dir.resolve("result");
        Path smpl_dir = root_dir.resolve("sample/pattern/" + demo);
        Path tmpl_dir = root_dir.resolve("template/pattern/" + demo);
        if (demo.endsWith("demo")) {
            smpl_dir = root_dir.resolve("sample/gui/" + demo);
            tmpl_dir = root_dir.resolve("template/app/gui/" + demo);
        }
        
        ArrayList<String> command = new ArrayList(Arrays.asList("java", "-javaagent:../lib/loggeragent.jar=time", "-cp", "bin", "Main"));
        for (int n = 1; n <= num_es; n++) {
            command.add(res_dir.resolve("java").resolve(demo + "_" + n + ".es").toString());
        }
        ProcessBuilder loggerBuilder = new ProcessBuilder(command);
        loggerBuilder.directory(new File("."));
        //loggerBuilder.inheritIO();
        //loggerBuilder.redirectOutput(ProcessBuilder.Redirect.INHERIT);
        File temp = new File("temp_colorchooser_demo.txt");
        loggerBuilder.redirectError(temp);
        Process logger = loggerBuilder.start();
        logger.waitFor();
        
        Queue<String> records = getInfo(temp, demo);
	if (records == null)
            return;
        //temp.delete();
        
        
        File[] samples = smpl_dir.toFile().listFiles();
        for (File child : samples) {
            String fname = child.getName();
            if (fname.startsWith("sample")) {
                //Queue<String> orig_sample = toQueue(child);
                Queue<String> mcs = extractMethodCalls(child, demo);
                Queue<String> mcalls = SampleProcessor.process(mcs);
                System.out.println("[debug] mcalls: " + mcalls);
                
                int num = Integer.parseInt(fname.substring(6, fname.indexOf(".")));
                System.out.println("Checking sample " + num + "...");
                
                //get the generated log for the current sample
                Queue<String> curr_log = new ArrayDeque<String>();
                String[] recarray = new String[records.size()];
                recarray = records.toArray(recarray);
                int i = 0;
                String simulator;
                if (demo.endsWith("demo"))
                    simulator = "Main.simulate";
                else
                    simulator = "Main." + demo + "_main" + num + "()";
                while (!recarray[i++].contains(simulator))
                    continue;
                while (!recarray[i].contains(simulator)){
                    curr_log.add(recarray[i++].trim().replaceAll("Adapted", "swings." + demo + "."));
                }
                
                //assert that the original sample is included in the generated log
                System.out.println("[debug] curr_log: " + curr_log);
                Assert.assertTrue("failure", included(mcalls, curr_log));
                System.out.println("Pass!");
            }
        }
        
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
    public boolean included(Queue<String> shorter, Queue<String> longer) {
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
    public boolean compare(String first, String second, Map<String, Integer> h1, Map<String, Integer> h2) {
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
    
    public String getPrototype(String orig, String[] hash) {
        for (int i = 0; i < hash.length; i++) {
            orig = orig.replaceFirst("@" + hash[i], "@obj");
        }
        return orig;
    }
    
    public String[] getHash(String log) {
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
    
    public Queue<String> getInfo(File f, String pattern)
    throws FileNotFoundException {
        Queue<String> output = new ArrayDeque<String>();
        
        Scanner sc = new Scanner(f);
        while (sc.hasNextLine()) {
            String curr = sc.nextLine();
	    System.out.println("line:" + curr);
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
    public Queue<String> extractMethodCalls(File file, String pattern)
    throws FileNotFoundException, IOException {
        Queue<String> el = new ArrayDeque<String>();
        
        Scanner reader = new Scanner(file);
        while (reader.hasNextLine()) {
            String curr = reader.nextLine();
            //skip commented items
            if (curr.contains("//")) continue;
            if (isMethodCall(curr, pattern))
                if (pattern.endsWith("demo")) {
                    String l = curr.trim();
                    el.add(l.replaceAll("\"", ""));
                }
                else
                    el.add(curr.trim().replaceAll("patterns." + pattern + ".", ""));
        }
        
        return el;
    }
    
    public boolean isMethodCall(String s, String pattern) {
        if (pattern.equals("observer"))
            return (s.contains("addObserver") || s.contains("dateChanged"));
        else if (pattern.endsWith("demo"))
            return ((s.contains("javax.swing") || s.contains("java.awt"))
                    && (! s.contains("invokeLater(")) && (! s.contains("pack")) );
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


