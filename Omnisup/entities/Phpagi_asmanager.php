<?php
 
  if(!class_exists('Phpagi'))
  {
    require_once(dirname(__FILE__) . DIRECTORY_SEPARATOR . 'Phpagi.php');
  }

  class Phpagi_asmanager
  {
    var $config;
    var $socket = NULL;
    var $server;
    var $port;
    var $pagi;
    var $event_handlers;
    
    function Phpagi_asmanager($config=NULL, $optconfig=array())
    {
      if(!is_null($config) && file_exists($config))
        $this->config = parse_ini_file($config, true);
      elseif(file_exists(DEFAULT_PHPAGI_CONFIG))
        $this->config = parse_ini_file(DEFAULT_PHPAGI_CONFIG, true);

      // If optconfig is specified, stuff vals and vars into 'asmanager' config array.
      foreach($optconfig as $var=>$val)
        $this->config['asmanager'][$var] = $val;

      // add default values to config for uninitialized values
      if(!isset($this->config['asmanager']['server'])) $this->config['asmanager']['server'] = 'localhost';
      if(!isset($this->config['asmanager']['port'])) $this->config['asmanager']['port'] = 5038;
      if(!isset($this->config['asmanager']['username'])) $this->config['asmanager']['username'] = 'phpagi';
      if(!isset($this->config['asmanager']['secret'])) $this->config['asmanager']['secret'] = 'phpagi';
    }

    function send_request($action, $parameters=array())
    {
      $req = "Action: $action\r\n";
      foreach($parameters as $var=>$val)
        $req .= "$var: $val\r\n";
      $req .= "\r\n";
      fwrite($this->socket, $req);
      return $this->wait_response();
    }

    function wait_response($allow_timeout=false)
    {
      $timeout = false;
      do
      {
        $type = NULL;
        $parameters = array();

        $buffer = trim(fgets($this->socket, 4096));
        while($buffer != '')
        {
          $a = strpos($buffer, ':');
          if($a)
          {
            if(!count($parameters)) // first line in a response?
            {
              $type = strtolower(substr($buffer, 0, $a));
              if(substr($buffer, $a + 2) == 'Follows')
              {
                // A follows response means there is a miltiline field that follows.
                $parameters['data'] = '';
                $buff = fgets($this->socket, 4096);
                while(substr($buff, 0, 6) != '--END ')
                {
                  $parameters['data'] .= $buff;
                  $buff = fgets($this->socket, 4096);
                }
              }
            }

            // store parameter in $parameters
            $parameters[substr($buffer, 0, $a)] = substr($buffer, $a + 2);
          }
          $buffer = trim(fgets($this->socket, 4096));
        }

        // process response
        switch($type)
        {
          case '': // timeout occured
            $timeout = $allow_timeout;
            break;
          case 'event':
            $this->process_event($parameters);
            break;
          case 'response':
            break;
          default:
            $this->log('Unhandled response packet from Manager: ' . print_r($parameters, true));
            break;
        }
      } while($type != 'response' && !$timeout);
      return $parameters;
    }

    function connect($server=NULL, $username=NULL, $secret=NULL)
    {
      // use config if not specified
      if(is_null($server)) $server = $this->config['asmanager']['server'];
      if(is_null($username)) $username = $this->config['asmanager']['username'];
      if(is_null($secret)) $secret = $this->config['asmanager']['secret'];

      // get port from server if specified
      if(strpos($server, ':') !== false)
      {
        $c = explode(':', $server);
        $this->server = $c[0];
        $this->port = $c[1];
      }
      else
      {
        $this->server = $server;
        $this->port = $this->config['asmanager']['port'];
      }

      // connect the socket, set a 10 second timeout for the connection, this gives us plenty of time to connect
      $errno = $errstr = NULL;
      $this->socket = @fsockopen($this->server, $this->port, $errno, $errstr, 10);
      if($this->socket == false)
      {
        $this->log("Unable to connect to manager {$this->server}:{$this->port} ($errno): $errstr");
        return false;
      } else
      // Set a 2 second timeout for read/write commands
      stream_set_timeout($this->socket, 2);
	
      // read the header
      $str = fgets($this->socket);
      if($str == false)
      {
        // a problem.
        $this->log("Asterisk Manager header not received.");
        return false;
      }
      else
      {
        // note: don't $this->log($str) until someone looks to see why it mangles the logging
      }

      // login
      $res = $this->send_request('login', array('Username'=>$username, 'Secret'=>$secret));
      if($res['Response'] != 'Success')
      {
        $this->log("Failed to login.");
        $this->disconnect(TRUE);
        return false;
      }
      return true;
    }

    function disconnect($dontlogoff=NULL)
    {
      if (!$dontlogoff)
      $this->logoff();
      fclose($this->socket);
    }

    function AbsoluteTimeout($channel, $timeout)
    {
      return $this->send_request('AbsoluteTimeout', array('Channel'=>$channel, 'Timeout'=>$timeout));
    }

   /**
    * Change monitoring filename of a channel
    *
    * @link http://www.voip-info.org/wiki-Asterisk+Manager+API+Action+ChangeMonitor
    * @param string $channel the channel to record.
    * @param string $file the new name of the file created in the monitor spool directory.
    */
    function ChangeMonitor($channel, $file)
    {
      return $this->send_request('ChangeMontior', array('Channel'=>$channel, 'File'=>$file));
    }

   /**
    * Execute Command
    *
    * @example examples/sip_show_peer.php Get information about a sip peer
    * @link http://www.voip-info.org/wiki-Asterisk+Manager+API+Action+Command
    * @link http://www.voip-info.org/wiki-Asterisk+CLI
    * @param string $command
    * @param string $actionid message matching variable
    */
    function Command($command, $actionid=NULL)
    {
      $parameters = array('Command'=>$command);
      if($actionid) $parameters['ActionID'] = $actionid;
      return $this->send_request('Command', $parameters);
    }

   /**
    * Enable/Disable sending of events to this manager
    *
    * @link http://www.voip-info.org/wiki-Asterisk+Manager+API+Action+Events
    * @param string $eventmask is either 'on', 'off', or 'system,call,log'
    */
    function Events($eventmask)
    {
      return $this->send_request('Events', array('EventMask'=>$eventmask));
    }

    function ExtensionState($exten, $context, $actionid=NULL)
    {
      $parameters = array('Exten'=>$exten, 'Context'=>$context);
      if($actionid) $parameters['ActionID'] = $actionid;
      return $this->send_request('ExtensionState', $parameters);
    }

    function GetVar($channel, $variable, $actionid=NULL)
    {
      $parameters = array('Channel'=>$channel, 'Variable'=>$variable);
      if($actionid) $parameters['ActionID'] = $actionid;
      return $this->send_request('GetVar', $parameters);
    }

    function Hangup($channel)
    {
      return $this->send_request('Hangup', array('Channel'=>$channel));
    }

    function IAXPeers()
    {
      return $this->send_request('IAXPeers');
    }

   /**
    * List available manager commands
    *
    * @link http://www.voip-info.org/wiki-Asterisk+Manager+API+Action+ListCommands
    * @param string $actionid message matching variable
    */
    function ListCommands($actionid=NULL)
    {
      if($actionid)
        return $this->send_request('ListCommands', array('ActionID'=>$actionid));
      else
        return $this->send_request('ListCommands');
    }

    function Logoff()
    {
      return $this->send_request('Logoff');
    }

    function MailboxCount($mailbox, $actionid=NULL)
    {
      $parameters = array('Mailbox'=>$mailbox);
      if($actionid) $parameters['ActionID'] = $actionid;
      return $this->send_request('MailboxCount', $parameters);
    }

    function MailboxStatus($mailbox, $actionid=NULL)
    {	
      $parameters = array('Mailbox'=>$mailbox);
      if($actionid) $parameters['ActionID'] = $actionid;
      return $this->send_request('MailboxStatus', $parameters);
    }

    function Monitor($channel, $file=NULL, $format=NULL, $mix=NULL)
    {
      $parameters = array('Channel'=>$channel);
      if($file) $parameters['File'] = $file;
      if($format) $parameters['Format'] = $format;
      if(!is_null($file)) $parameters['Mix'] = ($mix) ? 'true' : 'false';
      return $this->send_request('Monitor', $parameters);
    }

    function Originate($channel,
                       $exten=NULL, $context=NULL, $priority=NULL,
                       $application=NULL, $data=NULL,
                       $timeout=NULL, $callerid=NULL, $variable=NULL, $account=NULL, $async=NULL, $actionid=NULL)
    {
      $parameters = array('Channel'=>$channel);

      if($exten) $parameters['Exten'] = $exten;
      if($context) $parameters['Context'] = $context;
      if($priority) $parameters['Priority'] = $priority;

      if($application) $parameters['Application'] = $application;
      if($data) $parameters['Data'] = $data;

      if($timeout) $parameters['Timeout'] = $timeout;
      if($callerid) $parameters['CallerID'] = $callerid;
      if($variable) $parameters['Variable'] = $variable;
      if($account) $parameters['Account'] = $account;
      if(!is_null($async)) $parameters['Async'] = ($async) ? 'true' : 'false';
      if($actionid) $parameters['ActionID'] = $actionid;

      return $this->send_request('Originate', $parameters);
    }	

    function ParkedCalls($actionid=NULL)
    {
      if($actionid)
        return $this->send_request('ParkedCalls', array('ActionID'=>$actionid));
      else
        return $this->send_request('ParkedCalls');
    }

    function Ping()
    {
      return $this->send_request('Ping');
    }

    function QueueAdd($queue, $interface, $penalty=0)
    {
      $parameters = array('Queue'=>$queue, 'Interface'=>$interface);
      if($penalty) $parameters['Penalty'] = $penalty;
      return $this->send_request('QueueAdd', $parameters);
    }

    function QueueRemove($queue, $interface)
    {
      return $this->send_request('QueueRemove', array('Queue'=>$queue, 'Interface'=>$interface));
    }

    function Queues()
    {
      return $this->send_request('Queues');
    }

    function QueueStatus($actionid=NULL)
    {
      if($actionid)
        return $this->send_request('QueueStatus', array('ActionID'=>$actionid));
      else
        return $this->send_request('QueueStatus');
    }

    function Redirect($channel, $extrachannel, $exten, $context, $priority)
    {
      return $this->send_request('Redirect', array('Channel'=>$channel, 'ExtraChannel'=>$extrachannel, 'Exten'=>$exten,
                                                   'Context'=>$context, 'Priority'=>$priority));
    }

    function SetCDRUserField($userfield, $channel, $append=NULL)
    {
      $parameters = array('UserField'=>$userfield, 'Channel'=>$channel);
      if($append) $parameters['Append'] = $append;
      return $this->send_request('SetCDRUserField', $parameters);
    }

    function SetVar($channel, $variable, $value)
    {
      return $this->send_request('SetVar', array('Channel'=>$channel, 'Variable'=>$variable, 'Value'=>$value));
    }

    function Status($channel, $actionid=NULL)
    {
      $parameters = array('Channel'=>$channel);
      if($actionid) $parameters['ActionID'] = $actionid;
      return $this->send_request('Status', $parameters);
    }

    function StopMontor($channel)
    {
      return $this->send_request('StopMonitor', array('Channel'=>$channel));
    }

    function ZapDialOffhook($zapchannel, $number)
    {
      return $this->send_request('ZapDialOffhook', array('ZapChannel'=>$zapchannel, 'Number'=>$number));
    }

    function ZapDNDoff($zapchannel)
    {
      return $this->send_request('ZapDNDoff', array('ZapChannel'=>$zapchannel));
    }

    function ZapDNDon($zapchannel)
    {
      return $this->send_request('ZapDNDon', array('ZapChannel'=>$zapchannel));
    }

    function ZapHangup($zapchannel)
    {
      return $this->send_request('ZapHangup', array('ZapChannel'=>$zapchannel));
    }

    function ZapTransfer($zapchannel)
    {
      return $this->send_request('ZapTransfer', array('ZapChannel'=>$zapchannel));
    }

    function ZapShowChannels($actionid=NULL)
    {
      if($actionid)
        return $this->send_request('ZapShowChannels', array('ActionID'=>$actionid));
      else
        return $this->send_request('ZapShowChannels');
    }

    function log($message, $level=1)
    {
      if($this->pagi != false)
        $this->pagi->conlog($message, $level);
      else
        error_log(date('r') . ' - ' . $message);
    }

    function add_event_handler($event, $callback)
    {
      $event = strtolower($event);
      if(isset($this->event_handlers[$event]))
      {
        $this->log("$event handler is already defined, not over-writing.");
        return false;
      }
      $this->event_handlers[$event] = $callback;
      return true;
    }

    function process_event($parameters)
    {
      $ret = false;
      $e = strtolower($parameters['Event']);
      $this->log("Got event.. $e");		

      $handler = '';
      if(isset($this->event_handlers[$e])) $handler = $this->event_handlers[$e];
      elseif(isset($this->event_handlers['*'])) $handler = $this->event_handlers['*'];

      if(function_exists($handler))
      {
        $this->log("Execute handler $handler");
        $ret = $handler($e, $parameters, $this->server, $this->port);
      }
      else
        $this->log("No event handler for event '$e'");
      return $ret;
    }

	function database_show($family='') {
		$r = $this->command("database show $family");
		
		$data = explode("\n",$r["data"]);
		$db = array();
		
		// Remove the Privilege => Command initial entry that comes from the heading
		//
		array_shift($data);
		foreach ($data as $line) {
			$temp = explode(":",$line,2);
      if (trim($temp[0]) != '' && count($temp) == 2) {
				$temp[1] = isset($temp[1])?$temp[1]:null;
				$db[ trim($temp[0]) ] = trim($temp[1]);
			}
		}
		return $db;
	}
	
	function database_put($family, $key, $value) {
		$r = $this->command("database put ".str_replace(" ","/",$family)." ".str_replace(" ","/",$key)." ".$value);
		return (bool)strstr($r["data"], "success");
	}
	
	function database_get($family, $key) {
		$r = $this->command("database get ".str_replace(" ","/",$family)." ".str_replace(" ","/",$key));
		$data = strpos($r["data"],"Value:");
		if ($data !== false) {
			return trim(substr($r["data"],6+$data));
		} else {
			return false;
		}
	}
	
	function database_del($family, $key) {
		$r = $this->command("database del ".str_replace(" ","/",$family)." ".str_replace(" ","/",$key));
		return (bool)strstr($r["data"], "removed");
	}

}
?>
