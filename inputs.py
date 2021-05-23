import subprocess
import cfonts


#colors for terminal printing
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


#Parent function that handles the entire setup process
def setup_kali():
    drive=select_drive()
    confirm_drive_selection(drive=drive)
    wipe(drive=drive)
    image=select_and_verify_image(print_instructions=True)
    dd_image_onto_drive(image=image, drive=drive)
    set_up_persistence(image=image,drive=drive)
    finish()

#Show the fancy welcome banner
def welcome_banner():
    cfonts.say( text='Kali', font='3d',colors=['green'])
    print('----------------------')
    print('Welcome to Easy Kali!')
    print('This program was created to make it easy to boot Kali Linux to a drive or live USB.')
    print('Easy Kali makes it simple with y/n responses to quickly set up Kali to fit your needs')
    print('with options like persistence and encryption.')
    print('Press {} to get started.'.format(bcolors.OKGREEN+'enter'+bcolors.ENDC))
    print('----------------------')
    input('')


#Select which drive/drive you want to flash the os to
def select_drive():
    return input('Please enter the name of the drive (sda, sdb, sdc, ect.): ')

#Function that double checks your drive selection, you will erase everything on the drive so it is a good idea to sanity check this
def confirm_drive_selection(drive):
    print('')
    response=input('You entered {}, is this correct? y/n: '.format(bcolors.OKBLUE+drive+bcolors.ENDC))    
    if response=='y':
        pass
    elif response=='n':
        print('')
        setup_kali()
    else:
        print('Sorry, that input is not recognized.  Please type y/n.')
        confirm_drive_selection(drive=drive)
    print('----------------------')
    print('')


#wipe the drive if it is not empty to avoid partitioning and encryption errors
def wipe(drive):
    try:
        check=run_shell(check_output=True,call='lsblk /dev/{}'.format(drive))
    except:
        print('{}Sorry that drive was not found. Please check your drives and try again.{}'.format(bcolors.WARNING,bcolors.ENDC))
        print('')
        setup_kali()
    if 'part' in str(check):
        response=input('The drive {} is not empty, to avoid errors please wipe the drive before flashing. Would you like to wipe {} now? y/n: '.format(bcolors.OKBLUE+drive+bcolors.ENDC, bcolors.OKBLUE+drive+bcolors.ENDC))
        if response=='y':
            print('')
            print('Wiping {}, this might take a second depending on the size of your drive...'.format(bcolors.OKBLUE+drive+bcolors.ENDC))
            run_shell(output=True,call='sudo dd if=/dev/zero of=/dev/{} bs=50M status=progress'.format(drive))
        elif response=='n':
            print('')
            print('{}Exiting Easy-Kali, see you next time!{}'.format(bcolors.OKCYAN, bcolors.ENDC))
            print('')
            exit()
        else:
            print('Sorry, that input is not recognized.  Please type y/n: ')
            wipe(drive=drive)


#Select the file name that you want to flash to the drive
#Verify the Sha256 signature of the file
def select_and_verify_image(print_instructions=False):
    if print_instructions==True:
        print('Next, drag the Kali image into the root folder of Easy-Kali.')
    image=input('Please enter the full {} of the Kali Image: '.format(bcolors.OKBLUE+'file name'+bcolors.ENDC)).strip()
    print('')
    print('Verifying image Sha256 signature.  This will take a second...')
    sha256=subprocess.run(["shasum",'-a','256', image], stderr=subprocess.DEVNULL)
    if sha256.returncode==0:
        print('')
        input('Please check that the Sha256 Signature above matches your download from the official Kali Linux download link (https://www.kali.org/downloads/).  When you have confirmed its authenticity, press {} to continue.'.format(bcolors.OKGREEN+'enter'+bcolors.ENDC))
        print('----------------------')
        return image
    else:
        print('')
        print(bcolors.WARNING+'Please check the file name and try again. Make sure the image is in the Easy-Kali root folder.'+bcolors.ENDC)
        print('')
        return select_and_verify_image() 

#Flashes the image onto the drive with dd 
def dd_image_onto_drive(image,drive):
    print('')
    print('Please check all the info is correct')
    print(bcolors.BOLD+'Drive: '+bcolors.ENDC+bcolors.OKBLUE+drive+bcolors.ENDC)
    print(bcolors.BOLD+'Image: '+bcolors.ENDC+bcolors.OKBLUE+image+bcolors.ENDC)
    print('')
    response=input('While flashing Kali to the drive, everything on the drive will be erased. Do you want to continue? y/n: ')
    print('')
    if response=='y':
        print('Flashing {} to {}. Hang tight, this will take a second...'.format(bcolors.OKBLUE+image+bcolors.ENDC,bcolors.OKBLUE+drive+bcolors.ENDC))
        run_shell(output=True, call='sudo dd if={} of=/dev/{} bs=4M status=progress'.format(image,drive))
    elif response=='n':
        setup_kali()
    else:
        print('Sorry, that input is not recognized.  Please type y/n: ')
        dd_image_onto_drive(image=image, drive=drive)
    print('')
    print('{}Kali was successfully loaded onto your drive!{}'.format(bcolors.OKGREEN, bcolors.ENDC))
    print('----------------------')

#prompts user to select if they want persistence 
def set_up_persistence(drive,image):
    print('')
    response=input('Would you like to set up {}persistence{}? y/n: '.format(bcolors.OKBLUE,bcolors.ENDC))
    if response=='y':
        persistence_size(drive=drive, image=image)
    elif response=='n':
        pass
    else:
        print('Sorry, that input is not recognized.  Please type y/n.')

#select the size of the partition for persistence
def persistence_size(image,drive):
    print('')
    print('How much space would you like to partition for persistence?')
    partition_size=input('GiB: ')
    if type(int(partition_size)) is not int:
        print('Sorry, that input is not recognized.  Please type input an integer between {} and {}: '.format('i3092j09','09329023r'))
        persistence_size(drive=drive, image=image)
    print('')
    start_bytes=run_shell(check_output=True,call='read start _ < <(du -bcm {} | tail -1); echo $start'.format(image))
    start=int(str(start_bytes)[2:-3])
    run_shell(output=True,call='sudo parted -s /dev/{} mkpart primary {}MiB {}Mib'.format(drive,start,(int(partition_size)*1000)+start))
    print('----------------------')
    set_up_encryption(drive=drive)

#prompts the user to select if they want to encrypt the persistent partition
def set_up_encryption(drive):
    partition_drive=drive+str(3)
    print('')
    response=input('Would you like to set up encryption? y/n: ')
    if response=='y':
        encrypt(partition_drive=partition_drive)
    elif response=='n':
        print('Creating the partition for persistence, this might take a second...')
        run_shell(call='sudo mkfs.ext3 -L persistence /dev/{}'.format(partition_drive))
        run_shell(call='sudo e2label /dev/{} persistence'.format(partition_drive))
        run_shell(call='sudo mkdir -p /mnt/my_usb')
        run_shell(call='sudo mount /dev/{} /mnt/my_usb'.format(partition_drive))
        run_shell(call='sudo sh -c "echo "/ union" > persistence.conf"')
        run_shell(call='sudo umount /dev/{}'.format(partition_drive))
        print('----------------------')
    else:
        print('Sorry, that input is not recognized.  Please type y/n.')

#encrypt the persistent partition with Luks
def encrypt(partition_drive):
    print('Creating the encrypted partition for persistence, this might take a second...')
    run_shell(output=True, call='sudo cryptsetup --verbose --verify-passphrase luksFormat /dev/{}'.format(partition_drive))
    run_shell( output=True,call='sudo cryptsetup luksOpen /dev/{} my_usb'.format(partition_drive))
    print('Encrypting persistent partition, this will take a second...')
    run_shell(call='sudo mkfs.ext3 -L persistence /dev/mapper/my_usb')
    run_shell(call='sudo e2label /dev/mapper/my_usb persistence')
    run_shell(call='sudo mkdir -p /mnt/my_usb/')
    run_shell(call='sudo mount /dev/mapper/my_usb /mnt/my_usb')
    run_shell(call='sudo bash -c "echo / union > /mnt/my_usb/persistence.conf"')
    run_shell(call='sudo umount /dev/mapper/my_usb')
    run_shell(call='sudo cryptsetup luksClose /dev/mapper/my_usb')
    print('----------------------')

#display message to tell the user that everything is set up
def finish():
    print('')
    print('{}Everything is set up! You can eject your drive and boot it on any machine.  Happy hacking!{}'.format(bcolors.OKGREEN, bcolors.ENDC))
    print('')


#Function to call subprocess.run which runs commands in the terminal
#call: This is the actual command that is run in the terminal
#output: When True, this argument prints the output from each command. Some outputs are necessary to read.
#check_output: When True, the function returns the value from the call. This is useful for finding the starting point for the partition
def run_shell(call,output=False,check_output=False):
    if output:
        subprocess.run([call],shell=True,executable='bash')
    elif check_output:
        return subprocess.check_output([call], shell=True, executable='bash')
    else:   
        subprocess.run([call+' > /dev/null 2> /dev/null'],shell=True,executable='bash')

