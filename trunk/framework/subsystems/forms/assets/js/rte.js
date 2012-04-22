YUI().use('yui2-editor', 'node', function(Y) {

	/* See:
	 * http://yuiblog.com/sandbox/yui/3.2.0pr1/examples/yui/yui-gallery2.html
	 * http://jsfiddle.net/davglass/YmG7u/
	 * */

    Y.one('body').addClass('yui-skin-sam'); // For skinning
    var YAHOO = Y.YUI2, Dom = YAHOO.util.Dom, Event = YAHOO.util.Event;

    Y.all('.rich-text-editor').each(function(i) {

    	/* Below is from: http://developer.yahoo.com/yui/examples/editor/code_editor.html */

	    var myConfig = {
	            height: '300px',
	            width: '100%',
	            animate: true,
	            dompath: true,
	            focusAtStart: false
	        };
	
	        var state = 'off';
	        YAHOO.log('Set state to off..', 'info', 'example');
	
	        YAHOO.log('Create the Editor..', 'info', 'example');
	        var myEditor = new YAHOO.widget.Editor(i.get('id'), myConfig);
	        myEditor.on('toolbarLoaded', function() {
	            var codeConfig = {
	                type: 'push', label: 'Edit HTML Code', value: 'editcode'
	            };
	            YAHOO.log('Create the (editcode) Button', 'info', 'example');
	            this.toolbar.addButtonToGroup(codeConfig, 'insertitem');
	            
	            this.toolbar.on('editcodeClick', function() {
	                var ta = this.get('element'),
	                    iframe = this.get('iframe').get('element');
	
	                if (state == 'on') {
	                    state = 'off';
	                    this.toolbar.set('disabled', false);
	                    YAHOO.log('Show the Editor', 'info', 'example');
	                    YAHOO.log('Inject the HTML from the textarea into the editor', 'info', 'example');
	                    this.setEditorHTML(ta.value);
	                    if (!this.browser.ie) {
	                        this._setDesignMode('on');
	                    }
	
	                    Dom.removeClass(iframe, 'editor-hidden');
	                    Dom.addClass(ta, 'editor-hidden');
	                    this.show();
	                    this._focusWindow();
	                } else {
	                    state = 'on';
	                    YAHOO.log('Show the Code Editor', 'info', 'example');
	                    this.cleanHTML();
	                    YAHOO.log('Save the Editors HTML', 'info', 'example');
	                    Dom.addClass(iframe, 'editor-hidden');
	                    Dom.removeClass(ta, 'editor-hidden');
	                    this.toolbar.set('disabled', true);
	                    this.toolbar.getButtonByValue('editcode').set('disabled', false);
	                    this.toolbar.selectButton('editcode');
	                    this.dompath.innerHTML = 'Editing HTML Code';
	                    this.hide();
	                }
	                return false;
	            }, this, true);
	
	            this.on('cleanHTML', function(ev) {
	                YAHOO.log('cleanHTML callback fired..', 'info', 'example');
	                this.get('element').value = ev.html;
	            }, this, true);
	            
	            this.on('afterRender', function() {
	                var wrapper = this.get('editor_wrapper');
	                wrapper.appendChild(this.get('element'));
	                this.setStyle('width', '100%');
	                this.setStyle('height', '100%');
	                this.setStyle('visibility', '');
	                this.setStyle('top', '');
	                this.setStyle('left', '');
	                this.setStyle('position', '');

	                this.addClass('editor-hidden');
	            }, this, true);
	            
	            YAHOO.util.Event.on(window, 'load', YAHOO.util.Event.on(this.get('parentNode'), 'submit', function(ev, editor) {
				    editor.cleanHTML();
				    return true;
				}, this, true));

	        }, myEditor, true);

	        myEditor.render();

    });

});