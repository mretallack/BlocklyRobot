

function robot_forward(time) {

    $.ajax({

	    type: "POST",
	    url: "forward",
	    dataType: "json",
        async: false,
        contentType: "application/json; charset=utf-8",
	    data: JSON.stringify({
            time: time
        })
	});
}

function robot_left(time) {

    $.ajax({

	    type: "POST",
	    url: "left",
	    dataType: "json",
        async: false,
        contentType: "application/json; charset=utf-8",
	    data: JSON.stringify({
            time: time
        })
	});
}

function robot_right(time) {

    $.ajax({

	    type: "POST",
	    url: "right",
	    dataType: "json",
        async: false,
        contentType: "application/json; charset=utf-8",
	    data: JSON.stringify({
            time: time
        })
	});
}

function robot_finished() {

    var result=false;

    $.ajax({
        type: "GET",
        url: "finished",
        dataType: 'json',
        async: false,
        success: function(data) {
            result=data.finished;
        }
      })


    return result;
}

function robot_detect_obstacle() {

    var result=false;

    $.ajax({
        type: "GET",
        url: "detect",
        dataType: 'json',
        async: false,
        success: function(data) {
            result=data.detected;
        }
      })


    return result;
}


function create_tool(name, toolname) {

    // add in the move forward command
    Blockly.Blocks[name] = {
        init: function() {
          this.appendDummyInput()
              .appendField(toolname);
          this.appendDummyInput()
              .appendField(new Blockly.FieldNumber(0), "time");
          this.setPreviousStatement(true, null);
          this.setNextStatement(true, null);
          this.setColour(230);
       this.setTooltip("");
       this.setHelpUrl("");
        }
      };

    javascript.javascriptGenerator.forBlock[name] = function(block, generator) {
        var number_name = block.getFieldValue('time');
        // TODO: Assemble javascript into code variable.
        
        var code = name+'(' + number_name + ');\n';

		  	
        return code;
    };     

}

function create_bool_tool(name, toolname) {

    Blockly.Blocks[name] = {
        init: function() {
          this.appendDummyInput()
              .appendField(toolname);
          this.setOutput(true, "Boolean");
          this.setColour(230);
       this.setTooltip("");
       this.setHelpUrl("");
        }
      };


    javascript.javascriptGenerator.forBlock[name] = function(block) {
        // TODO: Assemble javascript into code variable.

        var code = name+'()';

        return [code, Blockly.JavaScript.ORDER_ADDITION];
    };
}


$(function() {

    var control_timer=null;

    // stop button is disabled by default
    $("#stopButton").attr("disabled", true);

    create_tool("robot_forward", "Move Forward")
    create_tool("robot_left", "Move Left")
    create_tool("robot_right", "Move Right")


    create_bool_tool("robot_finished", "Finished")
    create_bool_tool("robot_detect_obstacle", "Detect Obstacle")


	var workspacePlayground = Blockly.inject(document.getElementById('editor'), { toolbox: document.getElementById('toolbox') });

    // now get the current saved script

	$.ajax({

	    type: "GET",
	    url: "script",
	    dataType: "text",

	    success: function( data ) {

			try {

				xml =  Blockly.utils.xml.textToDom(data);
				workspacePlayground.clear();
				Blockly.Xml.domToWorkspace(xml, workspacePlayground);

			} catch (e) {
			}
	    }
	});


    $("#runButton").click(function(){

        $("#runButton").attr("disabled", true);
        $("#stopButton").attr("disabled", false);

        window.LoopTrap = 1000;

        Blockly.JavaScript.INFINITE_LOOP_TRAP =
            'if (--window.LoopTrap == 0) throw "Infinite loop.";\n';

        var code = Blockly.JavaScript.workspaceToCode(workspacePlayground);

        Blockly.JavaScript.INFINITE_LOOP_TRAP = null;

        try {

            if (control_timer!=null) {
                clearTimeout(control_timer);
                control_timer=null;
            }

            function run_control() { 
                eval(code);
                control_timer=setTimeout(run_control, 1000);
            }

            run_control();
          
        } catch (e) {
          alert(e);
        }
            
    });

    $("#stopButton").click(function(){
        if (control_timer!=null) {
            clearTimeout(control_timer);
            control_timer=null;
        }
        $("#runButton").attr("disabled", false);
        $("#stopButton").attr("disabled", true);
    });

    $("#saveButton").click(function(){

        // disable button to give user feedback
		$("#saveButton").attr("disabled", true);

		// ok, save the xml back
		var xml = Blockly.Xml.workspaceToDom(workspacePlayground);
		var data = Blockly.Xml.domToText(xml);

		// ok, save the src XML data
		$.ajax({
		    type: "PUT",
		    url: "script",
            contentType: "application/plain; charset=utf-8",
		    data: data,
		    error: function (xhr, ajaxOptions, thrownError) {
				// ok, save has not happened, so allow user to re-click
				$("#saveButton").attr("disabled", false);
		    },		    
		    success: function( data ) {
				$("#saveButton").attr("disabled", false);
		    },
			complete: function( data ) {
			}

		});	
            
    });

});
