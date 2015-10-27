package android.os;

public class MessageQueue {
  Message next();
  boolean enqueueMessage(Message msg, long when);
}
