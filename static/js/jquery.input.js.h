/*
$("input").bind("input", function (e) {
    $(this).next().text(this.value)
});
*/
(function($) {    
    // Handler for propertychange events only
    function propHandler () {
        var $this = $(this);
        if (window.event.propertyName == "value" && !$this.data("triggering.inputEvent")) {
            $this.data("triggering.inputEvent", true).trigger("input");
            window.setTimeout(function () {
                $this.data("triggering.inputEvent", false);
            }, 0);
        }
    }
    
    $.event.special.input = {
        setup: function(data, namespaces) {
            var timer,
                // Get a reference to the element
                elem  = this,
                // Store the current state of the element
                state = elem.value,
                // Create a dummy element that we can use for testing event support
                tester = document.createElement(this.tagName),
                // Check for native oninput
                oninput = "oninput" in tester || checkEvent(tester),
                // Check for onpropertychange
                onprop = "onpropertychange" in tester,
                // Generate a random namespace for event bindings
                ns = "inputEventNS" + ~~(Math.random() * 10000000),
                // Last resort event names
                evts = ["focus", "blur", "paste", "cut", "keydown", "drop", ""].join("."+ns+" ");

            function checkState () {
                var $this = $(elem);
                if (elem.value != state && !$this.data("triggering.inputEvent")) {
                    state = elem.value;

                    $this.data("triggering.inputEvent", true).trigger("input");
                    window.setTimeout(function () {
                        $this.data("triggering.inputEvent", false);
                    }, 0);
                }
            }
            
            // Set up a function to handle the different events that may fire
            function handler (e) {
                // When focusing, set a timer that polls for changes to the value
                if (e.type == "focus") {
                    checkState();
                    clearInterval(timer),
                    timer = window.setInterval(checkState, 250);
                }
                
                // When blurring, cancel the aforeset timer
                else if (e.type == "blur")
                    window.clearInterval(timer);
                
                // For all other events, queue a timer to check state ASAP
                else
                    window.setTimeout(checkState, 0);
            }
            
            // Bind to native event if available
            if (oninput)
                return false;
            
            // Else fall back to propertychange if available
            else if (onprop)
                $(this).find("input, textarea").andSelf().filter("input, textarea").bind("propertychange."+ns, propHandler);
            
            // Else clutch at straws!
            else
                $(this).find("input, textarea").andSelf().filter("input, textarea").bind(evts, handler);
            
            $(this).data("inputEventHandlerNS", ns);
        },
        teardown: function () {
            var elem = $(this);
            elem.find("input, textarea").unbind(elem.data("inputEventHandlerNS"));
            elem.data("inputEventHandlerNS", "");
        }
    };

    // Setup our jQuery shorthand method
    $.fn.input = function (handler) {
        return handler ? this.bind("input", handler) : this.trigger("input");
    }
    
    /*
       The following function tests the element for oninput support in Firefox.  Many thanks to
       http://blog.danielfriesen.name/2010/02/16/html5-browser-maze-oninput-support/
    */
    function checkEvent(el) {
        // First check, for if Firefox fixes its issue with el.oninput = function
        el.setAttribute("oninput", "return");
        if (typeof el.oninput == "function")
            return true;
        
        // Second check, because Firefox doesn't map oninput attribute to oninput property
        try {
            var e  = document.createEvent("KeyboardEvent"),
                ok = false,
                tester = function(e) {
                    ok = true;
                    e.preventDefault();
                    e.stopPropagation();
                }
            e.initKeyEvent("keypress", true, true, window, false, false, false, false, 0, "e".charCodeAt(0));
            document.body.appendChild(el);
            el.addEventListener("input", tester, false);
            el.focus();
            el.dispatchEvent(e);
            el.removeEventListener("input", tester, false);
            document.body.removeChild(el);
            return ok;
        } catch(e) {}
    }
})(jQuery);
