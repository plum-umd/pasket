import org.junit.Assert;

import java.nio.file.*;
import java.io.*;
import java.util.*;
import java.lang.reflect.*;


public class SanityChecker {
    
    public void sanityCheck(String demo)
    throws ClassNotFoundException, NoSuchMethodException,
    IllegalAccessException, InvocationTargetException,
    IOException, InterruptedException {
        Path root_dir = Paths.get(System.getProperty("user.dir")).getParent();
        Path res_dir = root_dir.resolve("result");
        Path smpl_dir = root_dir.resolve("sample/app/gui/" + demo);
        Path tmpl_dir = root_dir.resolve("template/app/gui/" + demo);
        
        
        ProcessBuilder loggerBuilder = new ProcessBuilder("java", "-javaagent:../lib/loggeragent.jar=time", "-cp", "bin", "Main");
        loggerBuilder.directory(new File("."));
        //loggerBuilder.inheritIO();
        //loggerBuilder.redirectOutput(ProcessBuilder.Redirect.INHERIT);
        File temp = new File("temp.txt");
        loggerBuilder.redirectError(temp);
        Process logger = loggerBuilder.start();
        logger.waitFor();
        
        Queue<String> records = getInfo(temp, demo);
        temp.delete();
        
        
        File[] samples = smpl_dir.toFile().listFiles();
        for (File child : samples) {
            String fname = child.getName();
            if (fname.startsWith("sample")) {
                //Queue<String> orig_sample = toQueue(child);
                Queue<String> mcalls = extractMethodCalls(child, demo);
                
                int num = Integer.parseInt(fname.substring(6, fname.indexOf(".")));
                System.out.println("Checking sample " + num + "...");
                
                //get the generated log for the current sample
                Queue<String> curr_log = new ArrayDeque<String>();
                String[] recarray = new String[records.size()];
                records.toArray(recarray);
                int i = 0;
                while (!recarray[i++].contains("Main.main" + num + "()"))
                    continue;
                while (!recarray[i].contains("Main.main" + num + "()"))
                    curr_log.add(recarray[i++]);
                
                //assert that the original sample is included in the generated log
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
        }
        
        return (!longer.isEmpty());
    }
    
    //check if the two logs are consistent w.r.t. the corresponding hash map
    public boolean compare(String first, String second, Map<String, Integer> h1, Map<String, Integer> h2) {
        String[] hash1 = getHash(first);
        String[] hash2 = getHash(second);
        if (hash1.length != hash2.length) return false;
        else if (! getPrototype(first, hash1).equals(getPrototype(second, hash2))) return false;
        else {
            for (int i = 0; i < hash1.length; i++) {
                if (! h1.containsKey(hash1[i]))
                    h1.put(hash1[i], new Integer(h1.size()));
                first = first.replaceFirst("@" + hash1[i], "obj_" + h1.get(hash1[i]));
                if (! h2.containsKey(hash2[i]))
                    h2.put(hash2[i], new Integer(h2.size()));
                second = second.replaceFirst("@" + hash2[i], "obj_" + h2.get(hash2[i]));
                
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
            orig = orig.replaceFirst("@" + hash[i], "obj");
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
            if (curr.contains("INFO: ")) output.add(curr.substring(6).trim().replaceAll("patterns." + pattern + ".", ""));
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
            if (isMethodCall(curr)) el.add(curr.trim().replaceAll("patterns." + pattern + ".", ""));
        }
        
        return el;
    }
    
    public boolean isMethodCall(String s) {
        return (s.contains("addObserver") || s.contains("dateChanged"));
    }
    
    public Event getEvent(String s) {
        String dt = s.substring(s.indexOf("(")+1, s.indexOf(")"));
        Event e = new Event();
        e.kind = 0;
        e.date = new Date(Integer.parseInt(dt));
        return e;
    }
    
}
