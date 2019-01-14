#!/usr/bin/perl
use strict;

package Disketo_Utils; 
my $VERSION=0.1;

use Exporter;
our @ISA = qw(Exporter);
our @EXPORT_OK = qw(go_recursivelly);

# Lists recursivelly all the subdirectories of given directory 
# and for each it calls the given anonymous function
sub go_recursivelly($&) {
	my $dir = shift @_;
	my $visitor = shift @_;
	
	my $continue = $visitor->($dir);
	if (!$continue) {
		return;
	}

	my $dh;
	unless (opendir($dh, $dir)) {
		print STDERR "Can't open $dir: $!";
		return(1);
	}

	while (my $child = readdir $dh) {
			if (substr($child, 0, 1) eq ".") {
				next;
			}
			
			my $subpath = "$dir/$child";
			if (!(-d $subpath)) {
				next;
			}
			if (!(-r $subpath)) {
				print STDERR "Cannot read $subpath!\n";
				next;
			}
		
			##print "$subpath\n";
			go_recursivelly($subpath, $visitor);
	}

	closedir $dh;
}

