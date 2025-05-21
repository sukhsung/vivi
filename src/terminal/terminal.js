
class Terminal {
    constructor( main_div, name ){
        this.div_main = main_div
        this.div_main.classList.add( "font-mono" )
        this.div_main.setAttribute('tabindex', 0)
        this.name = name

        // this.bc = broadcastchannel
        // this.bc.onmessage = (event) => {
        //     console.log( event['data'])
        //     this.onreceive_message( event['data'] )
        // }

        this.line_buffer = "> "
        this.history = ['clear','info']
        this.history_ind = 2


        this.div_result = document.createElement("div")
        this.div_main.appendChild( this.div_result)

        this.div_input = document.createElement("div")
        this.div_input.innerHTML = this.line_buffer
        this.div_main.appendChild( this.div_input)


        this.div_main.addEventListener('click', () => {
            this.onclick()
        })

        this.div_main.addEventListener('keydown', (e) => {
            this.onKeyPress(e)
        })

        this.print('Connect to Start: ')
        this.connected = false
        this.disconnect()

        this.query_connected()

    }

    onreceive_message( message ){
        if (message['func']=='connect'){
            if (message['value']) {
                this.connect()
            } else {
                this.disconnect()
            }
        } else if (message['func']=='command_return'){
            this.print( message['value'])
        } else if (message['type']=='connected'){
            console.log(message)
            if (message['value']) {
                this.connect()
            } else {
                this.disconnect()
            }
        }
    }

    connect( ){
        this.connected = true
        this.div_main.style.opacity = 1
        this.clear()
        this.print("Connected to Device")
    }
    disconnect(){
        this.connected = false
        this.div_main.style.opacity = 0.5
    }

    query_connected() {
        if (window.api.isConnected()){
            this.connect()
        } else {
            this.disconnect()
        }
    }

    //methods
    print( msg ){
        var newDiv = document.createElement("div")
        this.div_result.appendChild( newDiv )
        console.log(msg.length)
        msg = msg.split('\n')
        if (typeof msg == 'string') {
            newDiv.innerHTML += msg +"</br>"
        } else {
            msg.forEach(element => {
                newDiv.innerHTML += element +"</br>"
            });
        }
    }

    onKeyPress( e ) {
        if (this.connected) {
            if (e['ctrlKey'] && e['key']=='c'){
                this.line_buffer = '> '
            } else if ( e['key'].length == 1 ){
                this.line_buffer += e['key']
            } else if (e['key'] == 'Backspace') {
                this.lineBuffer_backspace()
            } else if (e['key'] == 'Enter') {
                this.lineBuffer_return()
                this.div_main.scrollTop = this.div_main.scrollHeight
            } else if (e['key'] == 'ArrowUp') {
                e.preventDefault()
                this.history_ind -= 1
                this.lineBuffer_history()
            } else if (e['key'] == 'ArrowDown') {
                e.preventDefault()
                this.history_ind += 1
                this.lineBuffer_history()
            } else {
                console.log(e)
            }

            this.div_input.innerHTML = this.line_buffer
            }

    }

    lineBuffer_history(){
        var new_line_buffer

        if (this.history.length ==0 ){
            this.history_ind = 0
            new_line_buffer = '> '
        } else if (this.history_ind < 0) {
            this.history_ind = -1
            new_line_buffer = '> '
        } else if (this.history_ind >= this.history.length) {
            this.history_ind = this.history.length
            new_line_buffer = '> '
        } else {
            new_line_buffer = '> '+this.history[this.history_ind]
        }

        this.line_buffer = new_line_buffer
    }

    lineBuffer_backspace(){
        if (this.line_buffer.length == 2){
            return
        } else {
            this.line_buffer = this.line_buffer.slice(0, -1)
        }
    }

    lineBuffer_return(){
        var msg = this.line_buffer.slice(2) 
        if (msg=="clear") {
            // this.print('')
            this.clear()
        } else if (msg=="info") {
            this.print('> info')
            this.print("terminal.js: Developed by Suk Hyun Sung, 2025")
        } else {
            this.return_action( msg )
            this.print( "> "+ msg )
        }

        if (msg.length >0 && this.history[this.history.length-1] != msg ){
            this.history.push(msg)
        }
        this.history_ind = this.history.length
        this.line_buffer = '> '
    }

    async return_action( line ) {
        console.log('msg was:' + line)
        var msg = {'origin':'terminal',
                   'func':'command',
                   'value':line
        }
        var res = await window.api.terminalCommand( msg )
        this.print(res)
    }

    clear() {
        while (this.div_result.firstChild) {
            this.div_result.removeChild(this.div_result.lastChild);
        }
    }

    onclick( ) {
        this.div_main.focus()
    }

    isActive() {
        return document.activeElement == this.div_main
    }
}

window.addEventListener("load", () => {
    div_term = document.getElementById( "terminal" )
    term = new Terminal(div_term, window.name)
})
