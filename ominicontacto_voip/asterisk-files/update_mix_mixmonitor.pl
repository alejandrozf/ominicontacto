#!/usr/bin/perl
use DBI;
use File::Path qw(mkpath);
use File::Basename;
use constant false => 0;
use constant true  => 1;
my %config;
my $dbh;

# If you want to run the tool in batch mode to process recordings that were
# not processed before, you can use a bash command like the following one.
# Be sure to su to the asterisk user before running it.
#
#for A in /var/spool/asterisk/monitor/q*; do fecha=`date +%Y-%m-%d -r $A`; unique=${A#*-}; uniqueid=${unique%.*}; echo "/usr/local/parselog/update_mix_mixmonitor_date.pl $uniqueid /var/spool/asterisk/monitor/$A $fecha"; done

# CONFIGURATION
# You have to set the proper database credentials
$config{'dbhost'} = 'localhost';
$config{'dbname'} = 'qstats';
$config{'dbuser'} = 'qstatsUser';
$config{'dbpass'} = 'qstatsPassw0rd';

# Destination directory for recordings
$config{'asterisk_spool'}  = "/var/spool/asterisk/monitor";
$config{'destination_dir'} = "/var/spool/asterisk/asternic";

$config{'move_recording'} = true;

# If you want "wav" recordings to be converted to .mp3 
# It requires the lame tool to be installed. You also must
# configure move_recordings above to true, as the mp3 file
# will be stored in a different path than asterisk defaults (destination_dir)

$config{'convertmp3'} = true;

# Do not modify bellow this line
my $LAME = `which lame 2>/dev/null`;
chomp($LAME);

sub connect_db() {
    my $return = 0;
    my %attr = (
        PrintError => 0,
        RaiseError => 0,
    );
    my $dsn = "DBI:mysql:database=$config{'dbname'};host=$config{'dbhost'}";
    $dbh->disconnect if $dbh;
    $dbh = DBI->connect( $dsn, $config{'dbuser'}, $config{'dbpass'}, \%attr ) or $return = 1;
    return $return;
}

&connect_db();

my $uniqueid             = $ARGV[0];
my $original_sound_file  = $ARGV[1];
my $passeddate           = $ARGV[2];

$original_sound_file     =~ s/wav49/WAV/g;

# We add the spool path to the original sound file
$original_sound_file     =~ s/$config{'asterisk_spool'}//g;
$original_sound_file     =~ s/^\///g;
$original_sound_file     = $config{'asterisk_spool'}."/".$original_sound_file;

# Extract filename and suffix for later processing
my($filename, $directories, $suffix) = fileparse($original_sound_file, "\.[^.]*");
$filename_nosuffix = $filename;
$filename = $filename.$suffix;
$filename_nosuffix =~ s/\+//g;
$filename =~ s/\+//g;

if($config{'move_recording'} == true) {

    my $firstletter = substr $filename, 0, 1;
    if ($firstletter ne "q" && $firstletter ne "o" ) { print "skip processing because first letter is $firstletter\n"; exit; }

# Set subdate destination directory
    $time = localtime(time);
    ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
    $datesubdir = sprintf ("%4d-%02d-%02d",$year+1900,$mon+1,$mday);

    if($passeddate ne "") {
        $datesubdir = $passeddate;
    }
    my $dest_directory     = $config{'destination_dir'}."/".$datesubdir;

# Create destination directory
    mkpath("$dest_directory");

# Set sql field
    $dest_sql           = $datesubdir."/".$filename;

    if($suffix eq ".wav" && $config{'convertmp3'} == true && $LAME ne "" && -f $LAME) {
# mp3 convertion if all conditions are met (config, lame installed, .wav file)
        my $file_mp3           = $filename_nosuffix.".mp3";
        my $dest_file_mp3      = $config{'destination_dir'}."/".$datesubdir."/".$file_mp3;
        my $temp_file_mp3      = $config{'asterisk_spool'}."/".$file_mp3;
        $dest_sql              = $datesubdir."/".$file_mp3;
        if ( -f $LAME ) {
            mkpath("$dest_directory");
            system("$LAME --silent -m m -b 8 --tt $original_sound_file --add-id3v2 $original_sound_file $temp_file_mp3");
            my $result = system("cp $temp_file_mp3 $dest_file_mp3");
            if($result==0) {
                system("rm -f $original_sound_file");
            }
            system("rm -f $temp_file_mp3");
        }
    } else {
# No convertion, just copy the file to destination directory
        my $dest_file_wav  = $config{'destination_dir'}."/".$datesubdir."/".$filename;
        my $result = system("cp $original_sound_file $dest_file_wav");
        if($result==0) {
            system("rm -f $original_sound_file");
        }
    }

} else {

    # Use the standard file location as stored in newer systems like FreePBX>=12
    $datesubdir = sprintf ("%4d-%02d-%02d",$year+1900,$mon+1,$mday);
    $dest_directory = $directories; 

    $dest_directory     =~ s/$config{'asterisk_spool'}//g;
    $dest_directory     =~ s/^\///g;

    $dest_sql       = $dest_directory.$filename;

}


# Update the DB
my $query = "REPLACE INTO recordings VALUES('$uniqueid','$dest_sql')";
$dbh->do($query);
$dbh->disconnect if $dbh;


#my $firstletter = substr $filename, 0, 1;
#if ($firstletter ne "q") { 
#    my $query = "UPDATE asteriskcdrdb.cdr SET userfield='$dest_sql' WHERE uniqueid='$uniqueid'";
#    $dbh->do($query);
#    $dbh->disconnect if $dbh;
#    exit; 
#
#} else {
#    # Update the DB
#    my $query = "REPLACE INTO recordings VALUES('$uniqueid','$dest_sql')";
#    $dbh->do($query);
#    $dbh->disconnect if $dbh;
#
#}
