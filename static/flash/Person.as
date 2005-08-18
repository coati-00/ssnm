class Person{

    private var name:String;
    private var supportLevel:Number;
    private var supportTypes:Array;
    private var supportTypesIcons:Array;
    private var xPos:Number;
    private var yPos:Number;
    private var container_mc:MovieClip;
    private var hit_mc:MovieClip;
    private var target_mc:MovieClip;
    private var name_txt:TextField;
    private var depth:Number;
    
/*
 +----------------------------------------------------------------+
 |                                                                |
 | The container_mc is the MovieClip object of the person class   |
 | that contains all the other objects.  Mouse interactions       |
 | work on this object.  Other objects are attached to it         |
 |                                                                |
 +----------------------------------------------------------------+
*/

    public function Person(theDepth:Number, target:MovieClip, x:Number, y:Number, theSupportLevel:Number){

        depth = theDepth;
        target_mc = target;
        supportTypes = new Array();
        container_mc = target_mc.createEmptyMovieClip("container_mc"+theDepth,theDepth);
        container_mc.createTextField("name_txt",1,2,2,36,14);

        var myStyle:TextFormat = new TextFormat("Tahoma",10);
        container_mc.name_txt.setNewTextFormat(myStyle);
        container_mc.name_txt.selectable = true;
        container_mc.name_txt.type = "input";

        // Reference to Person parent object from container_mc MovieClip object
        container_mc.parent = this;
        container_mc.tabEnabled = true;
        container_mc.focusEnabled = true;

        // Draw container object (may objectify this later to grow and shrink and template it)
        container_mc.lineStyle(1,0x336699);
        container_mc.moveTo(0,0);
        container_mc.beginFill(0x6699CC);
        container_mc.lineTo(40,0);
        container_mc.lineTo(40,40);
        container_mc.lineTo(0,40);
        container_mc.lineTo(0,0);
        container_mc.endFill();
       
        
        // make a hit area that doesnt intersect with the name or supports
        
        hit_mc = container_mc.createEmptyMovieClip("hit_mc",10);
        hit_mc.moveTo(0,16);
        hit_mc.beginFill(0x999999);
        hit_mc.lineTo(40,16);
        hit_mc.lineTo(40,35);
        hit_mc.lineTo(0,35);
        hit_mc.lineTo(0,16);
        hit_mc.endFill();

        hit_mc._alpha = 0;
        

        setSupportLevel(theSupportLevel);
        setPosition(x,y);

        // Attach behaviors to the container_mc MovieClip container object

/*        container_mc.onRollOver = function(){
            trace("over");
        }
*/        
        hit_mc.onRelease = function(){
            this._parent.stopDrag();
            this._parent.parent.setPosition(this._parent._x,this._parent._y);
            
            // Check if the drop location is legitimite
            // Draw a connecting line
            trace(this._parent.parent.toXML());
            //trace(this._parent._droptarget);
            if (this._parent._droptarget == "/trash"){
                //trace("yo");
                this._parent.parent.destroy();
            }
        }
        
        hit_mc.onPress = function(){
            //this.isTheOneBeingDragged = true;
            this._parent.startDrag(false);
            //trace(Selection.getFocus());
        }

        container_mc.name_txt.onSetFocus = function(){
            this.border = true;
        }
        
        container_mc.name_txt.onKillFocus = function(){
            this.border = false;
            this._parent.parent.setName(this.text);
        }

        container_mc.name_txt.onChanged = function(){
            // --BONUS --
            // maybe do an automatic resize of the object to fit the name
        }

        
    }
    
    public function destroy(){
    
        // kill the container and the rest goes away too
        container_mc.removeMovieClip();

    }
    
    
    public function setSupportLevel(theSupportLevel:Number){
        supportLevel = theSupportLevel;
        // visually update the container_mc to reflect the Support Level

        var colors = new Array(0xFF3333,0x33CC33,0x6699CC);

        container_mc.clear();

        container_mc.lineStyle(1,0x333333);
        container_mc.moveTo(0,0);
        container_mc.beginFill(colors[supportLevel]);
        container_mc.lineTo(40,0);
        container_mc.lineTo(40,40);
        container_mc.lineTo(0,40);
        container_mc.lineTo(0,0);
        container_mc.endFill();
    }

    public function getSupportLevel(){
        return supportLevel;
    }

    public function setName(theName:String){
        name = theName;
        container_mc.name_txt.text = theName;
    }
    
    public function getName(){
        return name;
    }

    public function addSupportType(theSupportType:String,icon:MovieClip){

        // FIX THIS.  MAKE IT A LOT BETTER!!!  (this for demo)

        // if the support type hasn't already been added:
        if (!supportTypes[theSupportType]){

            trace("add it");

            supportTypes[theSupportType] = true;
            
            if (theSupportType == "Financial"){
      
                // This will be a constructor soon..
                
                var stype1 = container_mc.createEmptyMovieClip("stype1",101);
        
                stype1.lineStyle(1,0x333333);
                stype1.moveTo(0,0);
                stype1.beginFill(0xFFFF00);
                stype1.lineTo(10,0);
                stype1.lineTo(10,10);
                stype1.lineTo(0,10);
                stype1.lineTo(0,0);
                stype1.endFill();
        
                stype1._x = 3;
                stype1._y = 35;
                
                supportTypesIcons[theSupportType] = stype1;

            } else {

                // This will be a constructor soon..
                
                var stype2 = container_mc.createEmptyMovieClip("stype2",102);
        
                stype2.lineStyle(1,0x333333);
                stype2.moveTo(0,0);
                stype2.beginFill(0x9C799B);
                stype2.lineTo(10,0);
                stype2.lineTo(10,10);
                stype2.lineTo(0,10);
                stype2.lineTo(0,0);
                stype2.endFill();
        
                stype2._x = 17;
                stype2._y = 35;
                
                supportTypesIcons[theSupportType] = stype2;
            }
            
            
            
            
            // attach supportType Icon to container_mc
            // be smart about it.  physically arrange them prettily

        }

    }
    
    public function getSupportTypes(){
        return supportTypes;
    }

    public function removeSupportType(theSupportType:String){
        delete supportTypes[theSupportType];

        // remove supportType Icon to container_mc
    }

    public function setPosition(x:Number, y:Number){
        xPos = x;
        yPos = y;
        container_mc._x = xPos;
        container_mc._y = yPos;
    }

    public function toXML(){
        var xmlString = "<person>";
        xmlString += "<name>" + name + "</name>";
        xmlString += "<supportLevel>" + supportLevel + "</supportLevel>";
        xmlString += "<supportTypes>";
        for (var supportType in supportTypes){
            xmlString += "<support>" + supportType + "</support>";
        }
        xmlString += "</supportTypes>";
        xmlString += "<x>" + xPos + "</x>";
        xmlString += "<y>" + yPos + "</y>";
        xmlString += "</person>";

        return xmlString;
    }
        
}