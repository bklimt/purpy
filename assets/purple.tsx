<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.8" tiledversion="1.8.0" name="purple" tilewidth="8" tileheight="8" tilecount="256" columns="16" backgroundcolor="#3d3846">
 <transformations hflip="0" vflip="0" rotate="0" preferuntransformed="1"/>
 <image source="purple.png" width="128" height="128"/>
 <tile id="128">
  <properties>
   <property name="bagel" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="129">
  <properties>
   <property name="direction" value="N"/>
   <property name="distance" type="int" value="0"/>
   <property name="platform" type="bool" value="true"/>
   <property name="speed" type="int" value="4"/>
  </properties>
 </tile>
 <tile id="130">
  <properties>
   <property name="deadly" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="131">
  <properties>
   <property name="deadly" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="132">
  <properties>
   <property name="direction" value="N"/>
   <property name="distance" type="int" value="0"/>
   <property name="platform" type="bool" value="true"/>
   <property name="speed" type="int" value="4"/>
  </properties>
 </tile>
 <tile id="133">
  <properties>
   <property name="direction" value="N"/>
   <property name="distance" type="int" value="0"/>
   <property name="platform" type="bool" value="true"/>
   <property name="speed" type="int" value="4"/>
  </properties>
 </tile>
 <tile id="136">
  <properties>
   <property name="condition" value="!red"/>
   <property name="switch" value="red"/>
  </properties>
 </tile>
 <tile id="137">
  <properties>
   <property name="alternate" type="int" value="153"/>
   <property name="condition" value="!red"/>
   <property name="solid" type="bool" value="false"/>
  </properties>
 </tile>
 <tile id="138">
  <properties>
   <property name="switch" value="~blue"/>
  </properties>
 </tile>
 <tile id="139">
  <properties>
   <property name="alternate" type="int" value="155"/>
   <property name="condition" value="!blue"/>
   <property name="solid" type="bool" value="false"/>
  </properties>
 </tile>
 <tile id="140">
  <properties>
   <property name="switch" value="green"/>
  </properties>
 </tile>
 <tile id="141">
  <properties>
   <property name="alternate" type="int" value="157"/>
   <property name="condition" value="!green"/>
   <property name="solid" type="bool" value="false"/>
  </properties>
 </tile>
 <tile id="142">
  <properties>
   <property name="switch" value="!green"/>
  </properties>
 </tile>
 <tile id="143">
  <properties>
   <property name="alternate" type="int" value="159"/>
   <property name="condition" value="green"/>
   <property name="solid" type="bool" value="false"/>
  </properties>
 </tile>
 <tile id="144">
  <properties>
   <property name="star" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="145">
  <properties>
   <property name="direction" value="N"/>
   <property name="distance" type="int" value="0"/>
   <property name="platform" type="bool" value="true"/>
   <property name="solid" type="bool" value="true"/>
   <property name="speed" type="int" value="4"/>
  </properties>
 </tile>
 <tile id="146">
  <properties>
   <property name="deadly" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="147">
  <properties>
   <property name="deadly" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="148">
  <properties>
   <property name="direction" value="N"/>
   <property name="distance" type="int" value="0"/>
   <property name="platform" type="bool" value="true"/>
   <property name="speed" type="int" value="4"/>
  </properties>
 </tile>
 <tile id="149">
  <properties>
   <property name="direction" value="N"/>
   <property name="distance" type="int" value="0"/>
   <property name="platform" type="bool" value="true"/>
   <property name="speed" type="int" value="4"/>
  </properties>
 </tile>
 <tile id="153">
  <properties>
   <property name="alternate" type="int" value="137"/>
   <property name="condition" value="red"/>
  </properties>
 </tile>
 <tile id="155">
  <properties>
   <property name="alternate" type="int" value="139"/>
   <property name="condition" value="blue"/>
  </properties>
 </tile>
 <tile id="157">
  <properties>
   <property name="alternate" type="int" value="141"/>
   <property name="condition" value="green"/>
  </properties>
 </tile>
 <tile id="159">
  <properties>
   <property name="alternate" type="int" value="143"/>
   <property name="condition" value="!green"/>
  </properties>
 </tile>
 <tile id="160">
  <properties>
   <property name="spiral" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="168">
  <properties>
   <property name="oneway" value="E"/>
  </properties>
 </tile>
 <tile id="169">
  <properties>
   <property name="oneway" value="W"/>
  </properties>
 </tile>
 <tile id="170">
  <properties>
   <property name="convey" value="E"/>
   <property name="solid" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="171">
  <properties>
   <property name="convey" value="E"/>
   <property name="solid" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="172">
  <properties>
   <property name="convey" value="W"/>
   <property name="solid" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="173">
  <properties>
   <property name="convey" value="W"/>
   <property name="solid" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="184">
  <properties>
   <property name="oneway" value="S"/>
  </properties>
 </tile>
 <tile id="185">
  <properties>
   <property name="oneway" value="N"/>
  </properties>
 </tile>
 <tile id="186">
  <properties>
   <property name="convey" value="E"/>
   <property name="solid" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="187">
  <properties>
   <property name="convey" value="E"/>
   <property name="solid" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="188">
  <properties>
   <property name="convey" value="W"/>
   <property name="solid" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="189">
  <properties>
   <property name="convey" value="W"/>
   <property name="solid" type="bool" value="true"/>
  </properties>
 </tile>
 <tile id="192">
  <properties>
   <property name="door" type="bool" value="true"/>
   <property name="stars_needed" type="int" value="0"/>
  </properties>
 </tile>
 <wangsets>
  <wangset name="Purple Edges" type="edge" tile="-1">
   <wangcolor name="Purple" color="#9141ac" tile="-1" probability="1"/>
   <wangcolor name="Green" color="#00ff00" tile="-1" probability="1"/>
   <wangtile tileid="0" wangid="0,0,1,0,1,0,0,0"/>
   <wangtile tileid="1" wangid="0,0,1,0,1,0,1,0"/>
   <wangtile tileid="2" wangid="0,0,0,0,1,0,1,0"/>
   <wangtile tileid="3" wangid="0,0,0,0,1,0,0,0"/>
   <wangtile tileid="4" wangid="1,0,1,0,1,0,1,0"/>
   <wangtile tileid="5" wangid="1,0,1,0,1,0,1,0"/>
   <wangtile tileid="8" wangid="2,0,1,0,1,0,2,0"/>
   <wangtile tileid="9" wangid="2,0,1,0,1,0,1,0"/>
   <wangtile tileid="10" wangid="2,0,2,0,1,0,1,0"/>
   <wangtile tileid="11" wangid="2,0,2,0,1,0,2,0"/>
   <wangtile tileid="16" wangid="1,0,1,0,1,0,0,0"/>
   <wangtile tileid="17" wangid="1,0,1,0,1,0,1,0"/>
   <wangtile tileid="18" wangid="1,0,0,0,1,0,1,0"/>
   <wangtile tileid="19" wangid="1,0,0,0,1,0,0,0"/>
   <wangtile tileid="20" wangid="1,0,1,0,1,0,1,0"/>
   <wangtile tileid="21" wangid="1,0,1,0,1,0,1,0"/>
   <wangtile tileid="24" wangid="1,0,1,0,1,0,2,0"/>
   <wangtile tileid="26" wangid="1,0,2,0,1,0,1,0"/>
   <wangtile tileid="27" wangid="1,0,2,0,1,0,2,0"/>
   <wangtile tileid="32" wangid="1,0,1,0,0,0,0,0"/>
   <wangtile tileid="33" wangid="1,0,1,0,0,0,1,0"/>
   <wangtile tileid="34" wangid="1,0,0,0,0,0,1,0"/>
   <wangtile tileid="35" wangid="1,0,0,0,0,0,0,0"/>
   <wangtile tileid="40" wangid="1,0,1,0,2,0,2,0"/>
   <wangtile tileid="41" wangid="1,0,1,0,2,0,1,0"/>
   <wangtile tileid="42" wangid="1,0,2,0,2,0,1,0"/>
   <wangtile tileid="43" wangid="1,0,2,0,2,0,2,0"/>
   <wangtile tileid="48" wangid="0,0,1,0,0,0,0,0"/>
   <wangtile tileid="49" wangid="0,0,1,0,0,0,1,0"/>
   <wangtile tileid="50" wangid="0,0,0,0,0,0,1,0"/>
   <wangtile tileid="56" wangid="2,0,1,0,2,0,2,0"/>
   <wangtile tileid="57" wangid="2,0,1,0,2,0,1,0"/>
   <wangtile tileid="58" wangid="2,0,2,0,2,0,1,0"/>
   <wangtile tileid="64" wangid="0,0,2,0,2,0,0,0"/>
   <wangtile tileid="65" wangid="0,0,2,0,2,0,2,0"/>
   <wangtile tileid="66" wangid="0,0,0,0,2,0,2,0"/>
   <wangtile tileid="67" wangid="0,0,0,0,2,0,0,0"/>
   <wangtile tileid="68" wangid="2,0,2,0,2,0,2,0"/>
   <wangtile tileid="69" wangid="2,0,2,0,2,0,2,0"/>
   <wangtile tileid="80" wangid="2,0,2,0,2,0,0,0"/>
   <wangtile tileid="81" wangid="2,0,2,0,2,0,2,0"/>
   <wangtile tileid="82" wangid="2,0,0,0,2,0,2,0"/>
   <wangtile tileid="83" wangid="2,0,0,0,2,0,0,0"/>
   <wangtile tileid="84" wangid="2,0,2,0,2,0,2,0"/>
   <wangtile tileid="85" wangid="2,0,2,0,2,0,2,0"/>
   <wangtile tileid="96" wangid="2,0,2,0,0,0,0,0"/>
   <wangtile tileid="97" wangid="2,0,2,0,0,0,2,0"/>
   <wangtile tileid="98" wangid="2,0,0,0,0,0,2,0"/>
   <wangtile tileid="99" wangid="2,0,0,0,0,0,0,0"/>
   <wangtile tileid="112" wangid="0,0,2,0,0,0,0,0"/>
   <wangtile tileid="113" wangid="0,0,2,0,0,0,2,0"/>
   <wangtile tileid="114" wangid="0,0,0,0,0,0,2,0"/>
  </wangset>
  <wangset name="Purple Corners" type="corner" tile="-1">
   <wangcolor name="Purple" color="#613583" tile="-1" probability="1"/>
   <wangcolor name="Green" color="#00ff00" tile="-1" probability="1"/>
   <wangtile tileid="0" wangid="0,0,0,1,0,0,0,0"/>
   <wangtile tileid="1" wangid="0,0,0,1,0,1,0,0"/>
   <wangtile tileid="2" wangid="0,0,0,0,0,1,0,0"/>
   <wangtile tileid="4" wangid="0,1,0,1,0,1,0,1"/>
   <wangtile tileid="5" wangid="0,1,0,1,0,1,0,1"/>
   <wangtile tileid="8" wangid="0,2,0,1,0,2,0,2"/>
   <wangtile tileid="9" wangid="0,2,0,1,0,1,0,2"/>
   <wangtile tileid="10" wangid="0,2,0,2,0,1,0,2"/>
   <wangtile tileid="16" wangid="0,1,0,1,0,0,0,0"/>
   <wangtile tileid="17" wangid="0,1,0,1,0,1,0,1"/>
   <wangtile tileid="18" wangid="0,0,0,0,0,1,0,1"/>
   <wangtile tileid="20" wangid="0,1,0,1,0,1,0,1"/>
   <wangtile tileid="21" wangid="0,1,0,1,0,1,0,1"/>
   <wangtile tileid="24" wangid="0,1,0,1,0,2,0,2"/>
   <wangtile tileid="26" wangid="0,2,0,2,0,1,0,1"/>
   <wangtile tileid="32" wangid="0,1,0,0,0,0,0,0"/>
   <wangtile tileid="33" wangid="0,1,0,0,0,0,0,1"/>
   <wangtile tileid="34" wangid="0,0,0,0,0,0,0,1"/>
   <wangtile tileid="36" wangid="0,1,0,0,0,1,0,1"/>
   <wangtile tileid="37" wangid="0,1,0,1,0,0,0,1"/>
   <wangtile tileid="38" wangid="0,0,0,1,0,0,0,1"/>
   <wangtile tileid="40" wangid="0,1,0,2,0,2,0,2"/>
   <wangtile tileid="41" wangid="0,1,0,2,0,2,0,1"/>
   <wangtile tileid="42" wangid="0,2,0,2,0,2,0,1"/>
   <wangtile tileid="44" wangid="0,1,0,2,0,1,0,1"/>
   <wangtile tileid="45" wangid="0,1,0,1,0,2,0,1"/>
   <wangtile tileid="46" wangid="0,2,0,1,0,2,0,1"/>
   <wangtile tileid="52" wangid="0,0,0,1,0,1,0,1"/>
   <wangtile tileid="53" wangid="0,1,0,1,0,1,0,0"/>
   <wangtile tileid="54" wangid="0,1,0,0,0,1,0,0"/>
   <wangtile tileid="60" wangid="0,2,0,1,0,1,0,1"/>
   <wangtile tileid="61" wangid="0,1,0,1,0,1,0,2"/>
   <wangtile tileid="62" wangid="0,1,0,2,0,1,0,2"/>
   <wangtile tileid="64" wangid="0,0,0,2,0,0,0,0"/>
   <wangtile tileid="65" wangid="0,0,0,2,0,2,0,0"/>
   <wangtile tileid="66" wangid="0,0,0,0,0,2,0,0"/>
   <wangtile tileid="68" wangid="0,2,0,2,0,2,0,2"/>
   <wangtile tileid="69" wangid="0,2,0,2,0,2,0,2"/>
   <wangtile tileid="72" wangid="0,0,0,2,0,1,0,0"/>
   <wangtile tileid="73" wangid="0,0,0,1,0,2,0,0"/>
   <wangtile tileid="74" wangid="0,1,0,2,0,0,0,0"/>
   <wangtile tileid="75" wangid="0,0,0,0,0,2,0,1"/>
   <wangtile tileid="80" wangid="0,2,0,2,0,0,0,0"/>
   <wangtile tileid="81" wangid="0,2,0,2,0,2,0,2"/>
   <wangtile tileid="82" wangid="0,0,0,0,0,2,0,2"/>
   <wangtile tileid="84" wangid="0,2,0,2,0,2,0,2"/>
   <wangtile tileid="85" wangid="0,2,0,2,0,2,0,2"/>
   <wangtile tileid="88" wangid="0,2,0,0,0,0,0,1"/>
   <wangtile tileid="89" wangid="0,1,0,0,0,0,0,2"/>
   <wangtile tileid="90" wangid="0,2,0,1,0,0,0,0"/>
   <wangtile tileid="91" wangid="0,0,0,0,0,1,0,2"/>
   <wangtile tileid="96" wangid="0,2,0,0,0,0,0,0"/>
   <wangtile tileid="97" wangid="0,2,0,0,0,0,0,2"/>
   <wangtile tileid="98" wangid="0,0,0,0,0,0,0,2"/>
   <wangtile tileid="100" wangid="0,2,0,0,0,2,0,2"/>
   <wangtile tileid="101" wangid="0,2,0,2,0,0,0,2"/>
   <wangtile tileid="102" wangid="0,2,0,0,0,2,0,0"/>
   <wangtile tileid="104" wangid="0,1,0,0,0,2,0,1"/>
   <wangtile tileid="105" wangid="0,1,0,2,0,0,0,1"/>
   <wangtile tileid="106" wangid="0,1,0,0,0,2,0,2"/>
   <wangtile tileid="107" wangid="0,2,0,2,0,0,0,1"/>
   <wangtile tileid="116" wangid="0,0,0,2,0,2,0,2"/>
   <wangtile tileid="117" wangid="0,2,0,2,0,2,0,0"/>
   <wangtile tileid="118" wangid="0,0,0,2,0,0,0,2"/>
   <wangtile tileid="120" wangid="0,0,0,1,0,1,0,2"/>
   <wangtile tileid="121" wangid="0,2,0,1,0,1,0,0"/>
   <wangtile tileid="122" wangid="0,0,0,1,0,2,0,2"/>
   <wangtile tileid="123" wangid="0,2,0,2,0,1,0,0"/>
  </wangset>
 </wangsets>
</tileset>
