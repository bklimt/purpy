<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.8" tiledversion="1.8.0" name="pastel" tilewidth="8" tileheight="8" tilecount="256" columns="16">
 <image source="pastel.png" width="128" height="128"/>
 <tile id="4">
  <properties>
   <property name="left_y" type="int" value="0"/>
   <property name="right_y" type="int" value="8"/>
   <property name="slope" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="20">
  <properties>
   <property name="left_y" type="int" value="8"/>
   <property name="right_y" type="int" value="0"/>
   <property name="slope" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="128">
  <properties>
   <property name="deadly" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="129">
  <properties>
   <property name="deadly" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="176">
  <properties>
   <property name="star" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="192">
  <properties>
   <property name="bagel" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="193">
  <properties>
   <property name="platform" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="208">
  <properties>
   <property name="solid" type="bool" value="true"/>
   <property name="spring" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="240">
  <properties>
   <property name="door" type="bool" value="true"/>
   <property name="stars_needed" type="int" value="1"/>
  </properties>
 </tile>
</tileset>
