#!/usr/bin/perl  -T

=head1 SYNOPSYS

searchOytser.pl keyword ...

Lists all the places each keyword appears in Stutshkov's "Oytser" along with
synonyms.

Author: Raphael Finkel 11/2004  GPL

=cut

use strict;
use CGI qw/:standard -debug/;
$ENV{'PATH'} = '/bin:/usr/bin:/usr/local/bin:/usr/local/gnu/bin'; # for security

# constants
my $dataFile = "/homes/raphael/y/oytser/oytser.yid";
my %expand = (
	s => 'substantiv',
	v => 'verb',
	ady => 'adyektiv',
	shpr => 'shprikhvort',
	fraz => 'frazeologye',
	inv => 'invaryant',
	
	shp => 'shpet-loshn',
	gn => 'gneyvim-loshn',
	kl => 'klezmer-loshn',
	am => 'amerikanizm',
	dyal => 'dyalektish',
	arkh => 'arkhaizm',
);
my $method = 'html'; # html or text
my $form = "
	<form
	action=\"searchOytser.cgi\"
	method=\"post\" enctype=\"multipart/form-data\">
		zukhverter (in YIVO Romanization, full words only; verbs in infinitive):
		<input type=\"text\" name=\"keys\" size=\"40\"
			autocorrect='off' autocapitalize='none'
			id=\"entry\"
			onmouseover=\"getElementById('entry').focus()\"
			/>
	</form>
	";

# variables
my $lineLength;

sub show {
	my ($section, $partOfSpeech, $text, $keyword) = @_;
	my ($component, $leader, $first);
	$text =~ s/\r//g;
	$text =~ s/\+/[vulgarizm] /g; 
	$text =~ s/\#/[nit rekomendirt] /g; 
	if ($method eq 'html') {
		print "<p>$section";
		if (length $partOfSpeech) {
			print " ($partOfSpeech)"
		}
		print "</p><br/>\n<ul>\n";
	} else { # text
		print "$section";
		if (length $partOfSpeech) {
			print " ($partOfSpeech)"
		}
		print "\n";
	}
	foreach $component (split(/;\s*/, $text)) {
		if ($method eq 'html') {
			# print STDERR "working on $text; keyword is $keyword\n";
			$component =~ s/</\&lt;/g;
			$component =~ s/($keyword)/<b style="background-color:#ffff66">$1<\/b>/g;
			print "<li>$component\n</li>\n";
		} else { # text
			$leader = ' ' x 4;
			while (length $component > $lineLength - (length($leader))) {
				my $breakPoint = # best to break at comma
					2+rindex($component, ',', $lineLength - (length($leader)));
				if ($breakPoint == 1) { # no comma; break at space
					$breakPoint = 
						1+rindex($component, ' ', $lineLength -
							(length($leader)));
				}
				$first = substr($component, 0, $breakPoint, '');
				print "$leader$first\n";
				$leader = ' ' x 8;
			}
			print "$leader$component\n";
		} # text
	} # each component
	if ($method eq 'html') {
		print "</ul>\n";
	}
} # show

sub expand {
	my ($list) = @_;
	my ($word);
	# print STDERR "expanding $list ";
	$list =~ s/-->/→ /; # introduce space so it splits
	foreach $word (split(/\s+/, $list)) {
		$list =~ s/\b$word\b/$expand{$word}/g if defined($expand{$word});
	}
	# print STDERR ": $list\n";
	return $list;
} # expand

sub oneWord {
	my ($keyword) = @_;
	# print STDERR "keyword is $keyword\n";
	$keyword =~ s/_/ /g;
	print h2($keyword), br();
	my ($line, $section, $page, $partOfSpeech);
	$section = "";
	seek OYTSER, 0, 0; # to start
	while (defined($line = <OYTSER>)) { # one line
		chomp $line;
		$line =~ s/^\s*//;
		if ($line =~ s/\[nr\. ([^]]*)\]\s*//) { 
			$section = $1;
			# print STDERR "section is $section\n";
			$partOfSpeech = "";
		}
		if ($line =~ s/\/(\d+[A-Z]?)\s*//g) { 
			$page = $1;
			# print STDERR "page is $page\n";
		}
		if ($line =~ s/\[([\w\s]+):\]\s*//) { 
			$partOfSpeech = expand($1);
		}
		$line =~ s/\[([->\w\s]+)\]/"[" . expand($1) .  "]"/eg;
		if ($line =~ /\b$keyword\b/) {
			$line =~
				s/\?(?=$keyword)/[nit rekomendirt in der kultur-shprakh:] /g;
			show($section, $partOfSpeech, $line, $keyword);
		}
	} # one line
} # oneWord

sub doSearch {
	my ($param, @args);
	$param = untaint(scalar param('keys'));
	print p("Use underscore (_) to connect words within a phrase.");
	print p("Thanks to Shimen Neuberg for entering all the data, " .
		"updated 9/2011.");
	if (defined($param)) {
		@args = split(/\s+/, $param);
	} else {
		@args = @ARGV;
	}
	while (@args) {
		my $keyword = shift @args;
		oneWord($keyword);
	}
} # doSearch

sub init {
	my ($title);
	$lineLength = (defined($1) ? $1 : 80) - 1;
	$title = untaint(scalar param('keys'));
	$title = 'oytser results' unless defined($title);
	$title = "Oytser" if $title eq '';
	my $analytics = `cat analytics.txt`;
	print header(-type=>"text/html", -expires=>'-1d', -charset=>'UTF-8') .
		start_html(-encoding=>"UTF-8",
			-title=>$title,
			-script=>$analytics,
			-meta=>{
				viewport=>"width=device-width, maximum-scale=1.0"
			},
		) .
		"<center>" .
		h1("Stutshkovs Oytser  סטוטשקאָװס אוצר") .
		"</center>" .
		$form . br() . hr() . br();
	open OYTSER, $dataFile or die("Can't open $dataFile.  Stopped");
} # init

sub finalize {
	$form =~ s/entry/entry1/g;
	print br(), hr(), br(), $form, end_html(), "\n";
	close OYTSER;
} # finalize

sub untaint {
	my ($string) = @_;
	$string =~ s/[^\w\s-]//g; # only alphabetic characters make sense.
	$string =~ /(.*)/; # remove taint
	$string = $1;
	# print STDERR "string [$string]\n";
	return ($string);
} # untaint

init();
doSearch();
finalize();

