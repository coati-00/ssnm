class Person{

    private var name:String;
    private var supportLevel:Number;
    private var supportTypes:Array;
    private var supTypes:Array;
    private var numSupports:Number;
    private var xPos:Number;
    private var yPos:Number;
    private var container_mc:MovieClip;
    private var hit_mc:MovieClip;
    private var target_mc:MovieClip;
    private var name_txt:TextField;
    private var depth:Number;
    private var deleted:Boolean;
    
    private var supportLevel_hit_mc:MovieClip;
    private var supportLevel_mc:MovieClip;

    private var constWidth:Number = 100;
    private var constHeight:Number = 41;
    private var constColors = new Array(0xFF3333,0xFBE52A,0x33CC33); //,0x6699CC);


    
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

        deleted = false;
        depth = theDepth;
        target_mc = target;
        supportTypes = new Array();
        supTypes = new Array();
        numSupports = 0;
        container_mc = target_mc.createEmptyMovieClip("container_mc"+theDepth,theDepth);
        container_mc.createTextField("name_txt",1,12,2,constWidth-14,30);

        var myStyle:TextFormat = new TextFormat("Tahoma",10);
        container_mc.name_txt.setNewTextFormat(myStyle);
        container_mc.name_txt.selectable = true;
        container_mc.name_txt.type = "input";
        container_mc.name_txt.multiline = true;
        container_mc.name_txt.wordWrap = true;

        // Reference to Person parent object from container_mc MovieClip object
        container_mc.parent = this;
        container_mc.tabEnabled = true;
        container_mc.focusEnabled = true;

        // Draw container object (may objectify this later to grow and shrink and template it)
        container_mc.lineStyle(1,0x336699);
        container_mc.moveTo(0,0);
        container_mc.beginFill(0x6699CC);
        container_mc.lineTo(constWidth,0);
        container_mc.lineTo(constWidth,constHeight);
        container_mc.lineTo(0,constHeight);
        container_mc.lineTo(0,0);
        container_mc.endFill();
       
        // Draw support level chooser toolbar
        supportLevel_mc = container_mc.createEmptyMovieClip("supportLevel_mc",11);

        addLevelSelector(supportLevel_mc,2);
        addLevelSelector(supportLevel_mc,1);
        addLevelSelector(supportLevel_mc,0);
        
        supportLevel_mc._alpha = 0;
        
        
        // make a hit area that doesnt intersect with the name or supports
        hit_mc = container_mc.createEmptyMovieClip("hit_mc",10);
        hit_mc.moveTo(10,13);
        hit_mc.beginFill(0x999999);
        hit_mc.lineTo(constWidth,12);
        hit_mc.lineTo(constWidth,constHeight-5);
        hit_mc.lineTo(10,constHeight-5);
        hit_mc.lineTo(10,12);
        hit_mc.endFill();

        hit_mc._alpha = 0;


        supportLevel_hit_mc = container_mc.createEmptyMovieClip("supportLevel_hit_mc",12);
        supportLevel_hit_mc.moveTo(0,0);
        supportLevel_hit_mc.beginFill(0x999999);
        supportLevel_hit_mc.lineTo(10,0);
        supportLevel_hit_mc.lineTo(10,constHeight);
        supportLevel_hit_mc.lineTo(0,constHeight);
        supportLevel_hit_mc.lineTo(0,0);
        supportLevel_hit_mc.endFill();
        
        supportLevel_hit_mc._alpha = 0;

        setSupportLevel(theSupportLevel);
        setPosition(x,y);
        setName("Click to change name");

        // Attach behaviors to the container_mc MovieClip container object


        supportLevel_hit_mc.onRollOver = function(){
            this._parent.supportLevel_mc._alpha = 100;
        }
        supportLevel_hit_mc.onRollOut = function(){
            this._parent.supportLevel_mc._alpha = 0;
        }
        supportLevel_hit_mc.onPress = function(){

            trace(this._ymouse);
            if (this._ymouse <= 12){
                this._parent.parent.setSupportLevel(2);
            }else if (this._ymouse >= 15 && this._ymouse <= 27){
                this._parent.parent.setSupportLevel(1);
            }else if (this._ymouse >= 30 && this._ymouse <= 42){
                this._parent.parent.setSupportLevel(0);
            }
        }


        hit_mc.onRelease = function(){
            this._parent.stopDrag();
            this._parent.parent.setPosition(this._parent._x,this._parent._y);
            
            // Check if the drop location is legitimite
            // Draw a connecting line
            //trace(this._parent.parent.toXML());
            //trace(this._parent._droptarget);
            
            if (this._parent._droptarget.indexOf("trash") != -1){
            //if (this._parent._droptarget == "/trash"){
                this._parent.parent.destroy();
            }
        }
        
        hit_mc.onPress = function(){
            //this.isTheOneBeingDragged = true;
            this._parent.startDrag(false);
            //trace(Selection.getFocus());
        }

        container_mc.name_txt.onSetFocus = function(){
            trace(Selection.getBeginIndex());
            trace(Selection.getEndIndex());
            //trace(this.text);
            //trace(Selection.getFocus());
            //trace(this.getCaretIndex());
            //Selection.setFocus(this);
            //this.setSelection(0,this.length);
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
    
    public function startDragging(){
        this.container_mc.startDrag(false);
    }

    public function stopDragging(){
        this.container_mc.hit_mc.onRelease();
    }

    
    public function destroy(){
    
        // kill the container and the rest goes away too
        container_mc.removeMovieClip();
        this.deleted = true;

    }
    
    public function isDeleted(){
        return (this.deleted);
    }
        
    
    private function addLevelSelector(theMovieClip:MovieClip, theSupportLevel:Number){
        
        var xPos:Number = 1;
        var yPos:Number = 15 * (2 - theSupportLevel)+1;
        var h:Number = 10;
        var w:Number = 10;

        theMovieClip.lineStyle(); //(1,constColors[theSupportLevel]);
        theMovieClip.moveTo(xPos+w,yPos);
        theMovieClip.beginFill(constColors[theSupportLevel]);
        theMovieClip.lineTo(xPos,yPos);
        theMovieClip.lineTo(xPos,yPos+h);
        theMovieClip.lineTo(xPos+w,yPos+h);
        theMovieClip.lineTo(xPos+w,yPos);
        theMovieClip.endFill();
        
        if (theSupportLevel == 0){
            theMovieClip.moveTo(xPos+(w/2),yPos+1);
            theMovieClip.beginFill(0x000000);
            theMovieClip.lineTo(xPos+w-1,yPos+(h/2));
            theMovieClip.lineTo(xPos+(w/2),yPos+h-1);
            theMovieClip.lineTo(xPos+1,yPos+(h/2));
            theMovieClip.lineTo(xPos+(w/2),yPos+1);
            theMovieClip.endFill();
        }else if (theSupportLevel == 1){
            theMovieClip.moveTo(xPos+2,yPos+2);
            theMovieClip.beginFill(0x000000);
            theMovieClip.lineTo(xPos+w-2,yPos+2);
            theMovieClip.lineTo(xPos+w-2,yPos+h-2);
            theMovieClip.lineTo(xPos+2,yPos+h-2);
            theMovieClip.lineTo(xPos+2,yPos+2);
            theMovieClip.endFill();
        }else if (theSupportLevel == 2){
            theMovieClip.beginFill(0x000000);
            theMovieClip.drawCircle([xPos+(w/2), yPos+(h/2)], w/2-2, 0x000000, 100, 0x000000, 0, 1); //drawArc(xPos+w-2,yPos+(h/2),(w/2)-2,360,0,(h/2)-2);
            theMovieClip.endFill();
        }    
    }
    
    public function setSupportLevel(theSupportLevel:Number){
        supportLevel = theSupportLevel;
        // visually update the container_mc to reflect the Support Level

        container_mc.clear();

        container_mc.lineStyle(1,0x333333);
        container_mc.moveTo(0,0);
        container_mc.beginFill(constColors[supportLevel]);
        container_mc.lineTo(constWidth,0);
        container_mc.lineTo(constWidth,constHeight);
        container_mc.lineTo(0,constHeight);
        container_mc.lineTo(0,0);
        container_mc.endFill();
        container_mc._alpha = 80;
        
        addLevelSelector(container_mc,supportLevel);
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

    public function addSupportType(theSupportType:String){
        // Add support to the array of supportTypes
        // Arrange the supportTypes objects on the Person object

        // if the support type hasn't already been added:
        if (!supportTypes[theSupportType]){

            trace("add: " + theSupportType);
            var support:SupportType = new SupportType(numSupports+100,container_mc,theSupportType,0,0,false);

            support.setPosition(numSupports*14+15,constHeight-7);

            supTypes[theSupportType] = support;
            supportTypes[theSupportType] = true;
            
            numSupports++;

        }

        for (var support in supTypes){
            trace(supTypes[support].getInfo());
        }

    }
    
    public function getSupportTypes(){
        // return named array of support types
        return supportTypes;
    }

    public function removeSupportType(theSupportType:String){

        trace("remove: " + theSupportType);
        delete supportTypes[theSupportType];
        delete supTypes[theSupportType];
        numSupports--;

        // reorganize the remaining supports and swap the depths
        var i:Number = 0;
        for (var support in supTypes){
            theSupportType = supTypes[support].getName();

            supTypes[support].setDepth(100+i);
            supTypes[support].setPosition(i*14+15,constHeight-7);
            i++;
        }

        for (var support in supTypes){
            trace(supTypes[support].getInfo());
        }

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