/* Copyright (C) 2018 Freetech Solutions

 This file is part of OMniLeads

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see http://www.gnu.org/licenses/.

*/

var PhoneFSM = new StateMachine.factory({
    init: 'Inactive',
    transitions: [
        // Inactive
      { name: 'start',                  from: 'Inactive',           to: 'Initial' },
        // Initial
      { name: 'registered',             from: 'Initial',            to: 'Ready' },
      { name: 'disconnected',           from: 'Initial',            to: 'End' },
      { name: 'failedRegistration',     from: 'Initial',            to: 'End' },
        // Ready
      { name: 'startCall',              from: 'Ready',              to: 'Calling' },
      { name: 'receiveCall',            from: 'Ready',              to: 'ReceivingCall' },
      { name: 'startPause',             from: 'Ready',              to: 'Paused' },
      { name: 'logout',                 from: 'Ready',              to: 'End' },
        // Calling
      { name: 'endCall',                from: 'Calling',            to: 'Ready' },
      { name: 'connectCall',            from: 'Calling',            to: 'OnCall' },
        // Paused
      { name: 'unpause',                from: 'Paused',             to: 'Ready' },
      { name: 'startCall',              from: 'Paused',             to: 'Calling' },
      { name: 'receiveCall',            from: 'Paused',             to: 'ReceivingCall' },
      { name: 'logout',                 from: 'Paused',             to: 'End' },
      { name: 'changePause',            from: 'Paused',             to: 'Paused' },
        // OnCall
      { name: 'endCall',                from: 'OnCall',             to: 'Ready' },
      { name: 'dialTransfer',           from: 'OnCall',             to: 'DialingTransfer' },
      { name: 'startOnHold',            from: 'OnCall',             to: 'OnHold' },
        // DialingTransfer
      { name: 'endCall',                from: 'DialingTransfer',    to: 'Ready' },
      { name: 'blindTransfer',          from: 'DialingTransfer',    to: 'Transfered' },
      { name: 'consultativeTransfer',   from: 'DialingTransfer',    to: 'Transfering' },
        // Transfered
      { name: 'endCall',                from: 'Transfered',         to: 'Ready' },
        // Transfering
      { name: 'transferAccepted',       from: 'Transfering',        to: 'Ready' },  // Cuando sucede?
      { name: 'endCall',                from: 'Transfering',        to: 'Ready' },
      { name: 'transferNotAccepted',    from: 'Transfering',        to: 'OnCall' }, // Cuando sucede?
      { name: 'endTransfer',            from: 'Transfering',        to: 'OnCall' },

        // ReceivingCall
      { name: 'acceptCall',             from: 'ReceivingCall',      to: 'OnCall' },
      { name: 'refuseCall',             from: 'ReceivingCall',      to: 'Ready' },
        // OnHold
      { name: 'releaseHold',            from: 'OnHold',             to: 'OnCall' },
      { name: 'endCall',                from: 'OnHold',             to: 'Ready' },
    ],

});

