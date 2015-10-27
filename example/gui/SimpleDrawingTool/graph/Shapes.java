/**
  This is the abstract parent class for different shape classes,
  like rectangle, oval, polygon and triangle. It provides an abstract
  method draw().
*/
package graph;

import java.util.*;
import java.awt.*;

public abstract class Shapes {

  /**abstract method draw()
    @return void
  */
  public abstract void draw(java.util.List list, Graphics g);

}
//different implementations of Shape class
class RectangleShape extends Shapes
{
  Point sPoint = null;
  Point ePoint = null;
  public void draw(java.util.List list, Graphics g)
  {
    Iterator it = list.iterator();
    //if the list does not contain the required two points, return.
    if(list.size()<2)
    {
      return;
    }
    sPoint = (Point)it.next();
    ePoint = (Point)it.next();
    if(sPoint == null || ePoint == null)
    {
      return;
    }
    else
    {
      g.fillRect((int)sPoint.getX(), (int)sPoint.getY(), (int)(ePoint.getX()-sPoint.getX()),
      (int)(ePoint.getY()-sPoint.getY()));
    }//end of if
    list.clear();
  }//end of draw for rectangle
}//rectangle

class OvalShape extends Shapes
{
  Point sPoint = null;
  Point ePoint = null;
  public void draw(java.util.List list, Graphics g)
  {
    Iterator it = list.iterator();
    //if the list does not contain the required two points, return.
    if(list.size()<2)
    {
      return;
    }
    sPoint = (Point)it.next();
    ePoint = (Point)it.next();
    if(sPoint == null || ePoint == null)
    {
      return;
    }
    else
    {
      g.fillOval((int)sPoint.getX(), (int)sPoint.getY(), (int)(ePoint.getX()-sPoint.getX()),
      (int)(ePoint.getY()-sPoint.getY()));
    }//end of if
    list.clear();
  }//end of draw for Oval
}//OvalShape
class TriangleShape extends Shapes
{
  public void draw(java.util.List list, Graphics g)
  {
    Point point = null;
    Iterator it = list.iterator();
    //if the list does not contain the required two points, return.
    if(list.size()<3)
    {
      return;
    }
    Polygon p = new Polygon();
    for(int i = 0; i < 3; i++)
    {
      point = (Point)it.next();
      p.addPoint((int)point.getX(), (int)point.getY());
    }

    g.fillPolygon(p);
    list.clear();
  }//end of draw for Triangle
}//Triangle
class PolygonShape extends Shapes
{
  public void draw(java.util.List list, Graphics g)
  {
    Point point = null;
    Iterator it = list.iterator();
    //if the list does not contain the required two points, return.
    if(list.size()<3)
    {
      return;
    }
    Polygon p = new Polygon();
    for(;it.hasNext();)
    {
      point = (Point)it.next();
      p.addPoint((int)point.getX(), (int)point.getY());
    }
    g.fillPolygon(p);
    list.clear();
  }//end of draw for Polygon
}//Polygon